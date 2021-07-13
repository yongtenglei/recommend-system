/*************************************************************************
 * Copyright (C) [2020] by Cambricon, Inc. All rights reserved
 *
 *  Licensed under the Apache License, Version 2.0 (the "License");
 *  you may not use this file except in compliance with the License.
 *  You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * The above copyright notice and this permission notice shall be included in
 * all copies or substantial portions of the Software.
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
 * OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
 * THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
 * THE SOFTWARE.
 *************************************************************************/
#include <memory>
#include <utility>
#include <vector>

#include "model_runner.hpp"

ModelRunner::ModelRunner(const std::shared_ptr<edk::ModelLoader>& model_loader,
                         int device_id)
  : model_loader_(model_loader), device_id_(device_id) {

  //1.momery init
  mem_op_.reset(new edk::MluMemoryOp);
  mem_op_->SetLoader(model_loader_);

  cpu_inputs_ = mem_op_->AllocCpuInput(batch_size_);
  mlu_inputs_ = mem_op_->AllocMluInput(batch_size_);
  cpu_outputs_ = mem_op_->AllocCpuOutput(batch_size_);
  mlu_outputs_ = mem_op_->AllocMluOutput(batch_size_);

  //2. easyinfer init
  infer_.reset(new edk::EasyInfer);
  infer_->Init(model_loader_, batch_size_, device_id);

}

ModelRunner::~ModelRunner() {
  if (nullptr != cpu_inputs_) {
    mem_op_->FreeCpuInput(cpu_inputs_);
    cpu_inputs_ = nullptr;
  }
  if (nullptr != mlu_inputs_) {
    mem_op_->FreeArrayMlu(mlu_inputs_, model_loader_->InputNum());
    mlu_inputs_ = nullptr;
  }
  if (nullptr != cpu_outputs_) {
    mem_op_->FreeCpuOutput(cpu_outputs_);
    cpu_outputs_ = nullptr;
  }
  if (nullptr != mlu_outputs_) {
    mem_op_->FreeArrayMlu(mlu_outputs_, model_loader_->OutputNum());
    mlu_outputs_ = nullptr;
  }
}

int ModelRunner::Run() {
  // do copy and inference
  mem_op_->MemcpyInputH2D(mlu_inputs_, cpu_inputs_, batch_size_);
  infer_->Run(mlu_inputs_, mlu_outputs_);
  mem_op_->MemcpyOutputD2H(cpu_outputs_, mlu_outputs_, batch_size_);
  return 0;
}

int ModelRunner::Run(const std::vector<NetInputs>& inputs, std::vector<NetOutputs>* outputs) {
  if (inputs.empty()) {
    return 0;
  }
  if (inputs[0].size() != model_loader_->InputNum()) {
    std::cout << "Input shapes do not match" << std::endl;
    return -1;
  }
  outputs->clear();

  uint32_t batch_size = model_loader_->InputShapes()[0].n;

  std::vector<NetInputs> batch_inputs;
  std::vector<NetOutputs> batch_outputs;
  for (size_t i = 0; i < inputs.size(); i += batch_size) {
    for (size_t j = 0; j < batch_size; ++j) {
      if (i + j < inputs.size()) {
        batch_inputs.push_back(inputs[i + j]);
      }
    }
    RunBatch(batch_inputs, &batch_outputs);
    outputs->insert(outputs->end(), batch_outputs.begin(), batch_outputs.end());
    batch_inputs.clear();
    batch_outputs.clear();
  }

  return 0;
}

int ModelRunner::RunBatch(const std::vector<NetInputs>& inputs, std::vector<NetOutputs>* outputs) {
  if (inputs.empty()) {
    return 0;
  }

  // prepare inputs
  for (size_t i = 0; i < inputs.size(); i++) {
    for (size_t j = 0; j < model_loader_->InputNum(); j++) {
      uint64_t data_count = model_loader_->InputShapes()[j].hwc();
      float* cpu_input = static_cast<float*>(cpu_inputs_[j]) + i * data_count;
      memcpy(cpu_input, inputs[i][j], data_count * sizeof(float));
    }
  }
  // do copy and inference
  mem_op_->MemcpyInputH2D(mlu_inputs_, cpu_inputs_, batch_size_);
  infer_->Run(mlu_inputs_, mlu_outputs_);
  mem_op_->MemcpyOutputD2H(cpu_outputs_, mlu_outputs_, batch_size_);

  // parse outputs
  for (size_t i = 0; i < inputs.size(); i++) {
    std::vector<std::vector<float>> output;
    for (size_t j = 0; j < model_loader_->OutputNum(); j++) {
      uint64_t data_count = model_loader_->OutputShapes()[j].hwc();
      float *cpu_output = static_cast<float *>(cpu_outputs_[j]) + i * data_count;
      output.push_back(std::vector<float>(cpu_output, cpu_output + data_count));
    }
    outputs->push_back(output);
  }

  return 0;
}
