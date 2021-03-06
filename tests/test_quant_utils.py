#
# Copyright (c) 2019 Intel Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import torch
import pytest
from distiller.quantization import q_utils as qu


def test_symmetric_qparams():
    with pytest.raises(ValueError):
        # Negative scalar
        qu.symmetric_linear_quantization_params(8, -5.)

        # Negative element in tensor
        qu.symmetric_linear_quantization_params(8, torch.tensor([-5., 10.]))

    # Scalar positive
    scale, zp = qu.symmetric_linear_quantization_params(8, 4.)
    assert not isinstance(scale, torch.Tensor)
    assert not isinstance(zp, torch.Tensor)
    assert scale == 31.75
    assert zp == 0

    # Scalar positive integer
    scale, zp = qu.symmetric_linear_quantization_params(8, 4)
    assert not isinstance(scale, torch.Tensor)
    assert not isinstance(zp, torch.Tensor)
    assert scale == 31.75
    assert zp == 0

    # Scalar zero
    scale, zp = qu.symmetric_linear_quantization_params(8, 0.)
    assert scale == 1
    assert zp == 0

    # Tensor positives
    sat = torch.tensor([4., 10.])
    scale, zp = qu.symmetric_linear_quantization_params(8, sat)
    assert torch.equal(scale, torch.tensor([31.75, 12.7]))
    assert torch.equal(zp, torch.zeros_like(sat))

    # Tensor positives - integer saturation values
    sat = torch.tensor([4, 10])
    scale, zp = qu.symmetric_linear_quantization_params(8, sat)
    assert torch.equal(scale, torch.tensor([31.75, 12.7]))
    assert torch.equal(zp, torch.zeros_like(sat, dtype=torch.float32))

    # Tensor with 0
    sat = torch.tensor([4., 0.])
    scale, zp = qu.symmetric_linear_quantization_params(8, sat)
    assert torch.equal(scale, torch.tensor([31.75, 1.]))
    assert torch.equal(zp, torch.zeros_like(sat))


def test_asymmetric_qparams():
    with pytest.raises(ValueError):
        # Test min > max
        # min scalar, max scalar
        qu.asymmetric_linear_quantization_params(8, 5., 4.)
        # min scalar, max tensor
        qu.asymmetric_linear_quantization_params(8, 5., torch.tensor([5., 3.]))
        # min tensor, max scalar
        qu.asymmetric_linear_quantization_params(8, torch.tensor([5., 3.]), 4.)
        # min tensor, max tensor
        qu.asymmetric_linear_quantization_params(8, torch.tensor([5., 3.]), torch.tensor([4., 7.]))

    # min scalar, max scalar

    # Min negative, max positive
    scale, zp = qu.asymmetric_linear_quantization_params(8, -2., 10., integral_zero_point=True, signed=False)
    assert not isinstance(scale, torch.Tensor)
    assert not isinstance(zp, torch.Tensor)
    assert scale == 21.25
    assert zp == -42

    scale, zp = qu.asymmetric_linear_quantization_params(8, -2., 10., integral_zero_point=True, signed=True)
    assert scale == 21.25
    assert zp == 86

    scale, zp = qu.asymmetric_linear_quantization_params(8, -2., 10., integral_zero_point=False, signed=False)
    assert scale == 21.25
    assert zp == -42.5

    scale, zp = qu.asymmetric_linear_quantization_params(8, -2., 10., integral_zero_point=False, signed=True)
    assert scale == 21.25
    assert zp == 85.5

    # Integer saturation values
    scale, zp = qu.asymmetric_linear_quantization_params(8, -2, 10, integral_zero_point=False, signed=True)
    assert scale == 21.25
    assert zp == 85.5

    # Both positive
    scale, zp = qu.asymmetric_linear_quantization_params(8, 5., 10.)
    assert scale == 25.5
    assert zp == 0

    # Both negative
    scale, zp = qu.asymmetric_linear_quantization_params(8, -10., -5.)
    assert scale == 25.5
    assert zp == -255

    # Both zero
    scale, zp = qu.asymmetric_linear_quantization_params(8, 0., 0.)
    assert scale == 1.
    assert zp == 0

    # min scalar, max tensor
    scale, zp = qu.asymmetric_linear_quantization_params(8, -10., torch.tensor([-2., 5.]))
    assert torch.equal(scale,torch.tensor([25.5, 17]))
    assert torch.equal(zp, torch.tensor([-255., -170]))

    scale, zp = qu.asymmetric_linear_quantization_params(8, 0., torch.tensor([0., 5.]))
    assert torch.equal(scale, torch.tensor([1., 51.]))
    assert torch.equal(zp, torch.tensor([0., 0.]))

    # Integer saturation values
    scale, zp = qu.asymmetric_linear_quantization_params(8, -10., torch.tensor([-2, 5]))
    assert torch.equal(scale, torch.tensor([25.5, 17]))
    assert torch.equal(zp, torch.tensor([-255., -170]))

    # min tensor, max scalar
    scale, zp = qu.asymmetric_linear_quantization_params(8, torch.tensor([-2., 5.]), 10.)
    assert torch.equal(scale, torch.tensor([21.25, 25.5]))
    assert torch.equal(zp, torch.tensor([-42., 0.]))

    scale, zp = qu.asymmetric_linear_quantization_params(8, torch.tensor([0., -5.]), 0.)
    assert torch.equal(scale, torch.tensor([1., 51.]))
    assert torch.equal(zp, torch.tensor([0., -255.]))

    # Integer saturation values
    scale, zp = qu.asymmetric_linear_quantization_params(8, torch.tensor([-2, 5]), 10.)
    assert torch.equal(scale, torch.tensor([21.25, 25.5]))
    assert torch.equal(zp, torch.tensor([-42., 0.]))

    # min tensor, max tensor
    scale, zp = qu.asymmetric_linear_quantization_params(8,
                                                         torch.tensor([-2., 5., -10., 0.]),
                                                         torch.tensor([10., 10., -5., 0.]))
    assert torch.equal(scale, torch.tensor([21.25, 25.5, 25.5, 1.]))
    assert torch.equal(zp, torch.tensor([-42., 0., -255., 0.]))
