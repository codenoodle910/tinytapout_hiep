# SPDX-License-Identifier: Apache-2.0
# Kiem tra ROM twiddle: doc du 128 dia chi va so voi bang FIPS 203 (dang Montgomery).

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles

Q = 3329
R = 1 << 16


def bitrev7(k):
    return int(f"{k:07b}"[::-1], 2)


# Gia tri ky vong tinh doc lap tu dinh nghia: zetas[k] = 17^BitRev7(k) mod q, nhan 2^16
EXPECTED = [pow(17, bitrev7(k), Q) * R % Q for k in range(128)]


def as_int(sig):
    v = sig.value
    return v.to_unsigned() if hasattr(v, "to_unsigned") else int(v)


@cocotb.test()
async def test_twiddle_rom(dut):
    dut._log.info("Start")
    clock = Clock(dut.clk, 10, unit="us")
    cocotb.start_soon(clock.start())

    dut.ena.value = 1
    dut.ui_in.value = 0
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    # Tu kiem tra bang ky vong voi cac gia tri da biet cua FIPS 203
    assert [pow(17, bitrev7(k), Q) for k in range(4)] == [1, 1729, 2580, 3289]

    for k in range(128):
        dut.ui_in.value = k
        # 1 chu ky chot dia chi + 1 chu ky chot du lieu, them 1 chu ky du phong
        await ClockCycles(dut.clk, 3)
        got = as_int(dut.uo_out) | ((as_int(dut.uio_out) & 0xF) << 8)
        assert got == EXPECTED[k], f"k={k}: doc {got}, ky vong {EXPECTED[k]}"

    # Chan uio[3:0] la ngo ra, uio[7:4] khong dung
    assert as_int(dut.uio_oe) == 0x0F

    dut._log.info("Ca 128 dia chi ROM deu dung")
