/*
 * Tiny Tapeout: ROM he so xoay (twiddle) cua NTT ML-KEM, 128 x 12 bit, dang Montgomery.
 * Muc dich: do dien tich ROM tren sky130.
 *
 *   ui_in[6:0]  : dia chi k (0..127)
 *   uo_out[7:0] : zeta[7:0]
 *   uio_out[3:0]: zeta[11:8]   (uio[3:0] la ngo ra, uio[7:4] khong dung)
 *
 * Dia chi va du lieu ra deu duoc chot bang flip-flop, nen ket qua xuat hien
 * 2 chu ky sau khi dat dia chi. Doi ten module theo ten GitHub cua ban.
 */
`default_nettype none

module tt_um_hiep_twiddle_rom (
    input  wire [7:0] ui_in,
    output wire [7:0] uo_out,
    input  wire [7:0] uio_in,
    output wire [7:0] uio_out,
    output wire [7:0] uio_oe,
    input  wire       ena,
    input  wire       clk,
    input  wire       rst_n
);
    reg  [6:0]  addr_q;
    reg  [11:0] zeta_q;
    wire [11:0] zeta;

    twiddle_rom u_rom (
        .addr (addr_q),
        .zeta (zeta)
    );

    always @(posedge clk) begin
        if (!rst_n) begin
            addr_q <= 7'd0;
            zeta_q <= 12'd0;
        end else begin
            addr_q <= ui_in[6:0];
            zeta_q <= zeta;
        end
    end

    assign uo_out  = zeta_q[7:0];
    assign uio_out = {4'b0000, zeta_q[11:8]};
    assign uio_oe  = 8'b0000_1111;

    // Bao cho linter biet cac chan khong dung la co chu dich
    wire _unused = &{ena, ui_in[7], uio_in, 1'b0};
endmodule
