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

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include <iostream>
#include <string>

#include "ranking.hpp"

namespace py = pybind11;

PYBIND11_MODULE(dataflow, m) {
  m.doc() = "dataflow python interface";

  pybind11::class_<UserInfo>(m, "UserInfo")
    .def(py::init())
    .def_readwrite("user", &UserInfo::user)
    .def_readwrite("item", &UserInfo::item)
    .def_readwrite("category", &UserInfo::category)
    .def_readwrite("history_behaviors", &UserInfo::history_behaviors);

  pybind11::class_<Ranking>(m, "Ranking")
    .def(py::init<const std::string&, const std::string&, const std::string&,
                  const std::string&, const std::string&, const std::string&,
                  const std::string&, const std::string&, int>())
    .def("process", &Ranking::Process);
}
