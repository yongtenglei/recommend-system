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

#ifndef MODULES_MODEL_RUNNER_INCLUDE_HPP_
#define MODULES_MODEL_RUNNER_INCLUDE_HPP_

#include <string.h>
#include <memory>
#include <string>
#include <utility>
#include <vector>

#include "easyinfer/easy_infer.h"
#include "easyinfer/mlu_context.h"
#include "easyinfer/mlu_memory_op.h"
#include "easyinfer/model_loader.h"

using NetInputs = std::vector<float*>;
using NetOutputs = std::vector<std::vector<float>>;

class ModelRunner {
 public:
  explicit ModelRunner(const std::shared_ptr<edk::ModelLoader>& model_loader, int device_id = 0);
  ~ModelRunner();
  void **GetCpuInputPtr() {return cpu_inputs_;}
  void **GetCpuOutputPtr() {return cpu_outputs_;}
  int Run();
  int Run(const std::vector<NetInputs>& inputs, std::vector<NetOutputs>* outputs);

 private:
  int RunBatch(const std::vector<NetInputs>& inputs, std::vector<NetOutputs>* outputs);
  std::shared_ptr<edk::ModelLoader> model_loader_;
  std::unique_ptr<edk::EasyInfer> infer_ = nullptr;
  std::unique_ptr<edk::MluMemoryOp> mem_op_ = nullptr;
  uint32_t batch_size_ = 1;
  int device_id_ = 0;
  void** cpu_inputs_ = nullptr;
  void** mlu_inputs_ = nullptr;
  void** cpu_outputs_ = nullptr;
  void** mlu_outputs_ = nullptr;

};

#endif  // MODULES_MODEL_RUNNER_INCLUDE_HPP_
