#include "pose.h"

namespace {
#define DIM 18
#define EDIM 18
#define MEDIM 18
typedef void (*Hfun)(double *, double *, double *);
const static double MAHA_THRESH_4 = 7.814727903251177;
const static double MAHA_THRESH_10 = 7.814727903251177;
const static double MAHA_THRESH_13 = 7.814727903251177;
const static double MAHA_THRESH_14 = 7.814727903251177;

/******************************************************************************
 *                      Code generated with SymPy 1.14.0                      *
 *                                                                            *
 *              See http://www.sympy.org/ for more information.               *
 *                                                                            *
 *                         This file is part of 'ekf'                         *
 ******************************************************************************/
void err_fun(double *nom_x, double *delta_x, double *out_5785056017088383392) {
   out_5785056017088383392[0] = delta_x[0] + nom_x[0];
   out_5785056017088383392[1] = delta_x[1] + nom_x[1];
   out_5785056017088383392[2] = delta_x[2] + nom_x[2];
   out_5785056017088383392[3] = delta_x[3] + nom_x[3];
   out_5785056017088383392[4] = delta_x[4] + nom_x[4];
   out_5785056017088383392[5] = delta_x[5] + nom_x[5];
   out_5785056017088383392[6] = delta_x[6] + nom_x[6];
   out_5785056017088383392[7] = delta_x[7] + nom_x[7];
   out_5785056017088383392[8] = delta_x[8] + nom_x[8];
   out_5785056017088383392[9] = delta_x[9] + nom_x[9];
   out_5785056017088383392[10] = delta_x[10] + nom_x[10];
   out_5785056017088383392[11] = delta_x[11] + nom_x[11];
   out_5785056017088383392[12] = delta_x[12] + nom_x[12];
   out_5785056017088383392[13] = delta_x[13] + nom_x[13];
   out_5785056017088383392[14] = delta_x[14] + nom_x[14];
   out_5785056017088383392[15] = delta_x[15] + nom_x[15];
   out_5785056017088383392[16] = delta_x[16] + nom_x[16];
   out_5785056017088383392[17] = delta_x[17] + nom_x[17];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_3431901073752666570) {
   out_3431901073752666570[0] = -nom_x[0] + true_x[0];
   out_3431901073752666570[1] = -nom_x[1] + true_x[1];
   out_3431901073752666570[2] = -nom_x[2] + true_x[2];
   out_3431901073752666570[3] = -nom_x[3] + true_x[3];
   out_3431901073752666570[4] = -nom_x[4] + true_x[4];
   out_3431901073752666570[5] = -nom_x[5] + true_x[5];
   out_3431901073752666570[6] = -nom_x[6] + true_x[6];
   out_3431901073752666570[7] = -nom_x[7] + true_x[7];
   out_3431901073752666570[8] = -nom_x[8] + true_x[8];
   out_3431901073752666570[9] = -nom_x[9] + true_x[9];
   out_3431901073752666570[10] = -nom_x[10] + true_x[10];
   out_3431901073752666570[11] = -nom_x[11] + true_x[11];
   out_3431901073752666570[12] = -nom_x[12] + true_x[12];
   out_3431901073752666570[13] = -nom_x[13] + true_x[13];
   out_3431901073752666570[14] = -nom_x[14] + true_x[14];
   out_3431901073752666570[15] = -nom_x[15] + true_x[15];
   out_3431901073752666570[16] = -nom_x[16] + true_x[16];
   out_3431901073752666570[17] = -nom_x[17] + true_x[17];
}
void H_mod_fun(double *state, double *out_4433155987963909288) {
   out_4433155987963909288[0] = 1.0;
   out_4433155987963909288[1] = 0.0;
   out_4433155987963909288[2] = 0.0;
   out_4433155987963909288[3] = 0.0;
   out_4433155987963909288[4] = 0.0;
   out_4433155987963909288[5] = 0.0;
   out_4433155987963909288[6] = 0.0;
   out_4433155987963909288[7] = 0.0;
   out_4433155987963909288[8] = 0.0;
   out_4433155987963909288[9] = 0.0;
   out_4433155987963909288[10] = 0.0;
   out_4433155987963909288[11] = 0.0;
   out_4433155987963909288[12] = 0.0;
   out_4433155987963909288[13] = 0.0;
   out_4433155987963909288[14] = 0.0;
   out_4433155987963909288[15] = 0.0;
   out_4433155987963909288[16] = 0.0;
   out_4433155987963909288[17] = 0.0;
   out_4433155987963909288[18] = 0.0;
   out_4433155987963909288[19] = 1.0;
   out_4433155987963909288[20] = 0.0;
   out_4433155987963909288[21] = 0.0;
   out_4433155987963909288[22] = 0.0;
   out_4433155987963909288[23] = 0.0;
   out_4433155987963909288[24] = 0.0;
   out_4433155987963909288[25] = 0.0;
   out_4433155987963909288[26] = 0.0;
   out_4433155987963909288[27] = 0.0;
   out_4433155987963909288[28] = 0.0;
   out_4433155987963909288[29] = 0.0;
   out_4433155987963909288[30] = 0.0;
   out_4433155987963909288[31] = 0.0;
   out_4433155987963909288[32] = 0.0;
   out_4433155987963909288[33] = 0.0;
   out_4433155987963909288[34] = 0.0;
   out_4433155987963909288[35] = 0.0;
   out_4433155987963909288[36] = 0.0;
   out_4433155987963909288[37] = 0.0;
   out_4433155987963909288[38] = 1.0;
   out_4433155987963909288[39] = 0.0;
   out_4433155987963909288[40] = 0.0;
   out_4433155987963909288[41] = 0.0;
   out_4433155987963909288[42] = 0.0;
   out_4433155987963909288[43] = 0.0;
   out_4433155987963909288[44] = 0.0;
   out_4433155987963909288[45] = 0.0;
   out_4433155987963909288[46] = 0.0;
   out_4433155987963909288[47] = 0.0;
   out_4433155987963909288[48] = 0.0;
   out_4433155987963909288[49] = 0.0;
   out_4433155987963909288[50] = 0.0;
   out_4433155987963909288[51] = 0.0;
   out_4433155987963909288[52] = 0.0;
   out_4433155987963909288[53] = 0.0;
   out_4433155987963909288[54] = 0.0;
   out_4433155987963909288[55] = 0.0;
   out_4433155987963909288[56] = 0.0;
   out_4433155987963909288[57] = 1.0;
   out_4433155987963909288[58] = 0.0;
   out_4433155987963909288[59] = 0.0;
   out_4433155987963909288[60] = 0.0;
   out_4433155987963909288[61] = 0.0;
   out_4433155987963909288[62] = 0.0;
   out_4433155987963909288[63] = 0.0;
   out_4433155987963909288[64] = 0.0;
   out_4433155987963909288[65] = 0.0;
   out_4433155987963909288[66] = 0.0;
   out_4433155987963909288[67] = 0.0;
   out_4433155987963909288[68] = 0.0;
   out_4433155987963909288[69] = 0.0;
   out_4433155987963909288[70] = 0.0;
   out_4433155987963909288[71] = 0.0;
   out_4433155987963909288[72] = 0.0;
   out_4433155987963909288[73] = 0.0;
   out_4433155987963909288[74] = 0.0;
   out_4433155987963909288[75] = 0.0;
   out_4433155987963909288[76] = 1.0;
   out_4433155987963909288[77] = 0.0;
   out_4433155987963909288[78] = 0.0;
   out_4433155987963909288[79] = 0.0;
   out_4433155987963909288[80] = 0.0;
   out_4433155987963909288[81] = 0.0;
   out_4433155987963909288[82] = 0.0;
   out_4433155987963909288[83] = 0.0;
   out_4433155987963909288[84] = 0.0;
   out_4433155987963909288[85] = 0.0;
   out_4433155987963909288[86] = 0.0;
   out_4433155987963909288[87] = 0.0;
   out_4433155987963909288[88] = 0.0;
   out_4433155987963909288[89] = 0.0;
   out_4433155987963909288[90] = 0.0;
   out_4433155987963909288[91] = 0.0;
   out_4433155987963909288[92] = 0.0;
   out_4433155987963909288[93] = 0.0;
   out_4433155987963909288[94] = 0.0;
   out_4433155987963909288[95] = 1.0;
   out_4433155987963909288[96] = 0.0;
   out_4433155987963909288[97] = 0.0;
   out_4433155987963909288[98] = 0.0;
   out_4433155987963909288[99] = 0.0;
   out_4433155987963909288[100] = 0.0;
   out_4433155987963909288[101] = 0.0;
   out_4433155987963909288[102] = 0.0;
   out_4433155987963909288[103] = 0.0;
   out_4433155987963909288[104] = 0.0;
   out_4433155987963909288[105] = 0.0;
   out_4433155987963909288[106] = 0.0;
   out_4433155987963909288[107] = 0.0;
   out_4433155987963909288[108] = 0.0;
   out_4433155987963909288[109] = 0.0;
   out_4433155987963909288[110] = 0.0;
   out_4433155987963909288[111] = 0.0;
   out_4433155987963909288[112] = 0.0;
   out_4433155987963909288[113] = 0.0;
   out_4433155987963909288[114] = 1.0;
   out_4433155987963909288[115] = 0.0;
   out_4433155987963909288[116] = 0.0;
   out_4433155987963909288[117] = 0.0;
   out_4433155987963909288[118] = 0.0;
   out_4433155987963909288[119] = 0.0;
   out_4433155987963909288[120] = 0.0;
   out_4433155987963909288[121] = 0.0;
   out_4433155987963909288[122] = 0.0;
   out_4433155987963909288[123] = 0.0;
   out_4433155987963909288[124] = 0.0;
   out_4433155987963909288[125] = 0.0;
   out_4433155987963909288[126] = 0.0;
   out_4433155987963909288[127] = 0.0;
   out_4433155987963909288[128] = 0.0;
   out_4433155987963909288[129] = 0.0;
   out_4433155987963909288[130] = 0.0;
   out_4433155987963909288[131] = 0.0;
   out_4433155987963909288[132] = 0.0;
   out_4433155987963909288[133] = 1.0;
   out_4433155987963909288[134] = 0.0;
   out_4433155987963909288[135] = 0.0;
   out_4433155987963909288[136] = 0.0;
   out_4433155987963909288[137] = 0.0;
   out_4433155987963909288[138] = 0.0;
   out_4433155987963909288[139] = 0.0;
   out_4433155987963909288[140] = 0.0;
   out_4433155987963909288[141] = 0.0;
   out_4433155987963909288[142] = 0.0;
   out_4433155987963909288[143] = 0.0;
   out_4433155987963909288[144] = 0.0;
   out_4433155987963909288[145] = 0.0;
   out_4433155987963909288[146] = 0.0;
   out_4433155987963909288[147] = 0.0;
   out_4433155987963909288[148] = 0.0;
   out_4433155987963909288[149] = 0.0;
   out_4433155987963909288[150] = 0.0;
   out_4433155987963909288[151] = 0.0;
   out_4433155987963909288[152] = 1.0;
   out_4433155987963909288[153] = 0.0;
   out_4433155987963909288[154] = 0.0;
   out_4433155987963909288[155] = 0.0;
   out_4433155987963909288[156] = 0.0;
   out_4433155987963909288[157] = 0.0;
   out_4433155987963909288[158] = 0.0;
   out_4433155987963909288[159] = 0.0;
   out_4433155987963909288[160] = 0.0;
   out_4433155987963909288[161] = 0.0;
   out_4433155987963909288[162] = 0.0;
   out_4433155987963909288[163] = 0.0;
   out_4433155987963909288[164] = 0.0;
   out_4433155987963909288[165] = 0.0;
   out_4433155987963909288[166] = 0.0;
   out_4433155987963909288[167] = 0.0;
   out_4433155987963909288[168] = 0.0;
   out_4433155987963909288[169] = 0.0;
   out_4433155987963909288[170] = 0.0;
   out_4433155987963909288[171] = 1.0;
   out_4433155987963909288[172] = 0.0;
   out_4433155987963909288[173] = 0.0;
   out_4433155987963909288[174] = 0.0;
   out_4433155987963909288[175] = 0.0;
   out_4433155987963909288[176] = 0.0;
   out_4433155987963909288[177] = 0.0;
   out_4433155987963909288[178] = 0.0;
   out_4433155987963909288[179] = 0.0;
   out_4433155987963909288[180] = 0.0;
   out_4433155987963909288[181] = 0.0;
   out_4433155987963909288[182] = 0.0;
   out_4433155987963909288[183] = 0.0;
   out_4433155987963909288[184] = 0.0;
   out_4433155987963909288[185] = 0.0;
   out_4433155987963909288[186] = 0.0;
   out_4433155987963909288[187] = 0.0;
   out_4433155987963909288[188] = 0.0;
   out_4433155987963909288[189] = 0.0;
   out_4433155987963909288[190] = 1.0;
   out_4433155987963909288[191] = 0.0;
   out_4433155987963909288[192] = 0.0;
   out_4433155987963909288[193] = 0.0;
   out_4433155987963909288[194] = 0.0;
   out_4433155987963909288[195] = 0.0;
   out_4433155987963909288[196] = 0.0;
   out_4433155987963909288[197] = 0.0;
   out_4433155987963909288[198] = 0.0;
   out_4433155987963909288[199] = 0.0;
   out_4433155987963909288[200] = 0.0;
   out_4433155987963909288[201] = 0.0;
   out_4433155987963909288[202] = 0.0;
   out_4433155987963909288[203] = 0.0;
   out_4433155987963909288[204] = 0.0;
   out_4433155987963909288[205] = 0.0;
   out_4433155987963909288[206] = 0.0;
   out_4433155987963909288[207] = 0.0;
   out_4433155987963909288[208] = 0.0;
   out_4433155987963909288[209] = 1.0;
   out_4433155987963909288[210] = 0.0;
   out_4433155987963909288[211] = 0.0;
   out_4433155987963909288[212] = 0.0;
   out_4433155987963909288[213] = 0.0;
   out_4433155987963909288[214] = 0.0;
   out_4433155987963909288[215] = 0.0;
   out_4433155987963909288[216] = 0.0;
   out_4433155987963909288[217] = 0.0;
   out_4433155987963909288[218] = 0.0;
   out_4433155987963909288[219] = 0.0;
   out_4433155987963909288[220] = 0.0;
   out_4433155987963909288[221] = 0.0;
   out_4433155987963909288[222] = 0.0;
   out_4433155987963909288[223] = 0.0;
   out_4433155987963909288[224] = 0.0;
   out_4433155987963909288[225] = 0.0;
   out_4433155987963909288[226] = 0.0;
   out_4433155987963909288[227] = 0.0;
   out_4433155987963909288[228] = 1.0;
   out_4433155987963909288[229] = 0.0;
   out_4433155987963909288[230] = 0.0;
   out_4433155987963909288[231] = 0.0;
   out_4433155987963909288[232] = 0.0;
   out_4433155987963909288[233] = 0.0;
   out_4433155987963909288[234] = 0.0;
   out_4433155987963909288[235] = 0.0;
   out_4433155987963909288[236] = 0.0;
   out_4433155987963909288[237] = 0.0;
   out_4433155987963909288[238] = 0.0;
   out_4433155987963909288[239] = 0.0;
   out_4433155987963909288[240] = 0.0;
   out_4433155987963909288[241] = 0.0;
   out_4433155987963909288[242] = 0.0;
   out_4433155987963909288[243] = 0.0;
   out_4433155987963909288[244] = 0.0;
   out_4433155987963909288[245] = 0.0;
   out_4433155987963909288[246] = 0.0;
   out_4433155987963909288[247] = 1.0;
   out_4433155987963909288[248] = 0.0;
   out_4433155987963909288[249] = 0.0;
   out_4433155987963909288[250] = 0.0;
   out_4433155987963909288[251] = 0.0;
   out_4433155987963909288[252] = 0.0;
   out_4433155987963909288[253] = 0.0;
   out_4433155987963909288[254] = 0.0;
   out_4433155987963909288[255] = 0.0;
   out_4433155987963909288[256] = 0.0;
   out_4433155987963909288[257] = 0.0;
   out_4433155987963909288[258] = 0.0;
   out_4433155987963909288[259] = 0.0;
   out_4433155987963909288[260] = 0.0;
   out_4433155987963909288[261] = 0.0;
   out_4433155987963909288[262] = 0.0;
   out_4433155987963909288[263] = 0.0;
   out_4433155987963909288[264] = 0.0;
   out_4433155987963909288[265] = 0.0;
   out_4433155987963909288[266] = 1.0;
   out_4433155987963909288[267] = 0.0;
   out_4433155987963909288[268] = 0.0;
   out_4433155987963909288[269] = 0.0;
   out_4433155987963909288[270] = 0.0;
   out_4433155987963909288[271] = 0.0;
   out_4433155987963909288[272] = 0.0;
   out_4433155987963909288[273] = 0.0;
   out_4433155987963909288[274] = 0.0;
   out_4433155987963909288[275] = 0.0;
   out_4433155987963909288[276] = 0.0;
   out_4433155987963909288[277] = 0.0;
   out_4433155987963909288[278] = 0.0;
   out_4433155987963909288[279] = 0.0;
   out_4433155987963909288[280] = 0.0;
   out_4433155987963909288[281] = 0.0;
   out_4433155987963909288[282] = 0.0;
   out_4433155987963909288[283] = 0.0;
   out_4433155987963909288[284] = 0.0;
   out_4433155987963909288[285] = 1.0;
   out_4433155987963909288[286] = 0.0;
   out_4433155987963909288[287] = 0.0;
   out_4433155987963909288[288] = 0.0;
   out_4433155987963909288[289] = 0.0;
   out_4433155987963909288[290] = 0.0;
   out_4433155987963909288[291] = 0.0;
   out_4433155987963909288[292] = 0.0;
   out_4433155987963909288[293] = 0.0;
   out_4433155987963909288[294] = 0.0;
   out_4433155987963909288[295] = 0.0;
   out_4433155987963909288[296] = 0.0;
   out_4433155987963909288[297] = 0.0;
   out_4433155987963909288[298] = 0.0;
   out_4433155987963909288[299] = 0.0;
   out_4433155987963909288[300] = 0.0;
   out_4433155987963909288[301] = 0.0;
   out_4433155987963909288[302] = 0.0;
   out_4433155987963909288[303] = 0.0;
   out_4433155987963909288[304] = 1.0;
   out_4433155987963909288[305] = 0.0;
   out_4433155987963909288[306] = 0.0;
   out_4433155987963909288[307] = 0.0;
   out_4433155987963909288[308] = 0.0;
   out_4433155987963909288[309] = 0.0;
   out_4433155987963909288[310] = 0.0;
   out_4433155987963909288[311] = 0.0;
   out_4433155987963909288[312] = 0.0;
   out_4433155987963909288[313] = 0.0;
   out_4433155987963909288[314] = 0.0;
   out_4433155987963909288[315] = 0.0;
   out_4433155987963909288[316] = 0.0;
   out_4433155987963909288[317] = 0.0;
   out_4433155987963909288[318] = 0.0;
   out_4433155987963909288[319] = 0.0;
   out_4433155987963909288[320] = 0.0;
   out_4433155987963909288[321] = 0.0;
   out_4433155987963909288[322] = 0.0;
   out_4433155987963909288[323] = 1.0;
}
void f_fun(double *state, double dt, double *out_6368947249978212614) {
   out_6368947249978212614[0] = atan2((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), -(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]));
   out_6368947249978212614[1] = asin(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]));
   out_6368947249978212614[2] = atan2(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), -(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]));
   out_6368947249978212614[3] = dt*state[12] + state[3];
   out_6368947249978212614[4] = dt*state[13] + state[4];
   out_6368947249978212614[5] = dt*state[14] + state[5];
   out_6368947249978212614[6] = state[6];
   out_6368947249978212614[7] = state[7];
   out_6368947249978212614[8] = state[8];
   out_6368947249978212614[9] = state[9];
   out_6368947249978212614[10] = state[10];
   out_6368947249978212614[11] = state[11];
   out_6368947249978212614[12] = state[12];
   out_6368947249978212614[13] = state[13];
   out_6368947249978212614[14] = state[14];
   out_6368947249978212614[15] = state[15];
   out_6368947249978212614[16] = state[16];
   out_6368947249978212614[17] = state[17];
}
void F_fun(double *state, double dt, double *out_8244575924748074855) {
   out_8244575924748074855[0] = ((-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*cos(state[0])*cos(state[1]) - sin(state[0])*cos(dt*state[6])*cos(dt*state[7])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + ((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*cos(state[0])*cos(state[1]) - sin(dt*state[6])*sin(state[0])*cos(dt*state[7])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_8244575924748074855[1] = ((-sin(dt*state[6])*sin(dt*state[8]) - sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*cos(state[1]) - (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*sin(state[1]) - sin(state[1])*cos(dt*state[6])*cos(dt*state[7])*cos(state[0]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*sin(state[1]) + (-sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) + sin(dt*state[8])*cos(dt*state[6]))*cos(state[1]) - sin(dt*state[6])*sin(state[1])*cos(dt*state[7])*cos(state[0]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_8244575924748074855[2] = 0;
   out_8244575924748074855[3] = 0;
   out_8244575924748074855[4] = 0;
   out_8244575924748074855[5] = 0;
   out_8244575924748074855[6] = (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(dt*cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*sin(dt*state[8]) - dt*sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-dt*sin(dt*state[6])*cos(dt*state[8]) + dt*sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) - dt*cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (dt*sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_8244575924748074855[7] = (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[6])*sin(dt*state[7])*cos(state[0])*cos(state[1]) + dt*sin(dt*state[6])*sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) - dt*sin(dt*state[6])*sin(state[1])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[7])*cos(dt*state[6])*cos(state[0])*cos(state[1]) + dt*sin(dt*state[8])*sin(state[0])*cos(dt*state[6])*cos(dt*state[7])*cos(state[1]) - dt*sin(state[1])*cos(dt*state[6])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_8244575924748074855[8] = ((dt*sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + dt*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (dt*sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + ((dt*sin(dt*state[6])*sin(dt*state[8]) + dt*sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*cos(dt*state[8]) + dt*sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_8244575924748074855[9] = 0;
   out_8244575924748074855[10] = 0;
   out_8244575924748074855[11] = 0;
   out_8244575924748074855[12] = 0;
   out_8244575924748074855[13] = 0;
   out_8244575924748074855[14] = 0;
   out_8244575924748074855[15] = 0;
   out_8244575924748074855[16] = 0;
   out_8244575924748074855[17] = 0;
   out_8244575924748074855[18] = (-sin(dt*state[7])*sin(state[0])*cos(state[1]) - sin(dt*state[8])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_8244575924748074855[19] = (-sin(dt*state[7])*sin(state[1])*cos(state[0]) + sin(dt*state[8])*sin(state[0])*sin(state[1])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_8244575924748074855[20] = 0;
   out_8244575924748074855[21] = 0;
   out_8244575924748074855[22] = 0;
   out_8244575924748074855[23] = 0;
   out_8244575924748074855[24] = 0;
   out_8244575924748074855[25] = (dt*sin(dt*state[7])*sin(dt*state[8])*sin(state[0])*cos(state[1]) - dt*sin(dt*state[7])*sin(state[1])*cos(dt*state[8]) + dt*cos(dt*state[7])*cos(state[0])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_8244575924748074855[26] = (-dt*sin(dt*state[8])*sin(state[1])*cos(dt*state[7]) - dt*sin(state[0])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_8244575924748074855[27] = 0;
   out_8244575924748074855[28] = 0;
   out_8244575924748074855[29] = 0;
   out_8244575924748074855[30] = 0;
   out_8244575924748074855[31] = 0;
   out_8244575924748074855[32] = 0;
   out_8244575924748074855[33] = 0;
   out_8244575924748074855[34] = 0;
   out_8244575924748074855[35] = 0;
   out_8244575924748074855[36] = ((sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[7]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[7]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_8244575924748074855[37] = (-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(-sin(dt*state[7])*sin(state[2])*cos(state[0])*cos(state[1]) + sin(dt*state[8])*sin(state[0])*sin(state[2])*cos(dt*state[7])*cos(state[1]) - sin(state[1])*sin(state[2])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*(-sin(dt*state[7])*cos(state[0])*cos(state[1])*cos(state[2]) + sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1])*cos(state[2]) - sin(state[1])*cos(dt*state[7])*cos(dt*state[8])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_8244575924748074855[38] = ((-sin(state[0])*sin(state[2]) - sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (-sin(state[0])*sin(state[1])*sin(state[2]) - cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_8244575924748074855[39] = 0;
   out_8244575924748074855[40] = 0;
   out_8244575924748074855[41] = 0;
   out_8244575924748074855[42] = 0;
   out_8244575924748074855[43] = (-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(dt*(sin(state[0])*cos(state[2]) - sin(state[1])*sin(state[2])*cos(state[0]))*cos(dt*state[7]) - dt*(sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[7])*sin(dt*state[8]) - dt*sin(dt*state[7])*sin(state[2])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*(dt*(-sin(state[0])*sin(state[2]) - sin(state[1])*cos(state[0])*cos(state[2]))*cos(dt*state[7]) - dt*(sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[7])*sin(dt*state[8]) - dt*sin(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_8244575924748074855[44] = (dt*(sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*cos(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*sin(state[2])*cos(dt*state[7])*cos(state[1]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + (dt*(sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*cos(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[7])*cos(state[1])*cos(state[2]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_8244575924748074855[45] = 0;
   out_8244575924748074855[46] = 0;
   out_8244575924748074855[47] = 0;
   out_8244575924748074855[48] = 0;
   out_8244575924748074855[49] = 0;
   out_8244575924748074855[50] = 0;
   out_8244575924748074855[51] = 0;
   out_8244575924748074855[52] = 0;
   out_8244575924748074855[53] = 0;
   out_8244575924748074855[54] = 0;
   out_8244575924748074855[55] = 0;
   out_8244575924748074855[56] = 0;
   out_8244575924748074855[57] = 1;
   out_8244575924748074855[58] = 0;
   out_8244575924748074855[59] = 0;
   out_8244575924748074855[60] = 0;
   out_8244575924748074855[61] = 0;
   out_8244575924748074855[62] = 0;
   out_8244575924748074855[63] = 0;
   out_8244575924748074855[64] = 0;
   out_8244575924748074855[65] = 0;
   out_8244575924748074855[66] = dt;
   out_8244575924748074855[67] = 0;
   out_8244575924748074855[68] = 0;
   out_8244575924748074855[69] = 0;
   out_8244575924748074855[70] = 0;
   out_8244575924748074855[71] = 0;
   out_8244575924748074855[72] = 0;
   out_8244575924748074855[73] = 0;
   out_8244575924748074855[74] = 0;
   out_8244575924748074855[75] = 0;
   out_8244575924748074855[76] = 1;
   out_8244575924748074855[77] = 0;
   out_8244575924748074855[78] = 0;
   out_8244575924748074855[79] = 0;
   out_8244575924748074855[80] = 0;
   out_8244575924748074855[81] = 0;
   out_8244575924748074855[82] = 0;
   out_8244575924748074855[83] = 0;
   out_8244575924748074855[84] = 0;
   out_8244575924748074855[85] = dt;
   out_8244575924748074855[86] = 0;
   out_8244575924748074855[87] = 0;
   out_8244575924748074855[88] = 0;
   out_8244575924748074855[89] = 0;
   out_8244575924748074855[90] = 0;
   out_8244575924748074855[91] = 0;
   out_8244575924748074855[92] = 0;
   out_8244575924748074855[93] = 0;
   out_8244575924748074855[94] = 0;
   out_8244575924748074855[95] = 1;
   out_8244575924748074855[96] = 0;
   out_8244575924748074855[97] = 0;
   out_8244575924748074855[98] = 0;
   out_8244575924748074855[99] = 0;
   out_8244575924748074855[100] = 0;
   out_8244575924748074855[101] = 0;
   out_8244575924748074855[102] = 0;
   out_8244575924748074855[103] = 0;
   out_8244575924748074855[104] = dt;
   out_8244575924748074855[105] = 0;
   out_8244575924748074855[106] = 0;
   out_8244575924748074855[107] = 0;
   out_8244575924748074855[108] = 0;
   out_8244575924748074855[109] = 0;
   out_8244575924748074855[110] = 0;
   out_8244575924748074855[111] = 0;
   out_8244575924748074855[112] = 0;
   out_8244575924748074855[113] = 0;
   out_8244575924748074855[114] = 1;
   out_8244575924748074855[115] = 0;
   out_8244575924748074855[116] = 0;
   out_8244575924748074855[117] = 0;
   out_8244575924748074855[118] = 0;
   out_8244575924748074855[119] = 0;
   out_8244575924748074855[120] = 0;
   out_8244575924748074855[121] = 0;
   out_8244575924748074855[122] = 0;
   out_8244575924748074855[123] = 0;
   out_8244575924748074855[124] = 0;
   out_8244575924748074855[125] = 0;
   out_8244575924748074855[126] = 0;
   out_8244575924748074855[127] = 0;
   out_8244575924748074855[128] = 0;
   out_8244575924748074855[129] = 0;
   out_8244575924748074855[130] = 0;
   out_8244575924748074855[131] = 0;
   out_8244575924748074855[132] = 0;
   out_8244575924748074855[133] = 1;
   out_8244575924748074855[134] = 0;
   out_8244575924748074855[135] = 0;
   out_8244575924748074855[136] = 0;
   out_8244575924748074855[137] = 0;
   out_8244575924748074855[138] = 0;
   out_8244575924748074855[139] = 0;
   out_8244575924748074855[140] = 0;
   out_8244575924748074855[141] = 0;
   out_8244575924748074855[142] = 0;
   out_8244575924748074855[143] = 0;
   out_8244575924748074855[144] = 0;
   out_8244575924748074855[145] = 0;
   out_8244575924748074855[146] = 0;
   out_8244575924748074855[147] = 0;
   out_8244575924748074855[148] = 0;
   out_8244575924748074855[149] = 0;
   out_8244575924748074855[150] = 0;
   out_8244575924748074855[151] = 0;
   out_8244575924748074855[152] = 1;
   out_8244575924748074855[153] = 0;
   out_8244575924748074855[154] = 0;
   out_8244575924748074855[155] = 0;
   out_8244575924748074855[156] = 0;
   out_8244575924748074855[157] = 0;
   out_8244575924748074855[158] = 0;
   out_8244575924748074855[159] = 0;
   out_8244575924748074855[160] = 0;
   out_8244575924748074855[161] = 0;
   out_8244575924748074855[162] = 0;
   out_8244575924748074855[163] = 0;
   out_8244575924748074855[164] = 0;
   out_8244575924748074855[165] = 0;
   out_8244575924748074855[166] = 0;
   out_8244575924748074855[167] = 0;
   out_8244575924748074855[168] = 0;
   out_8244575924748074855[169] = 0;
   out_8244575924748074855[170] = 0;
   out_8244575924748074855[171] = 1;
   out_8244575924748074855[172] = 0;
   out_8244575924748074855[173] = 0;
   out_8244575924748074855[174] = 0;
   out_8244575924748074855[175] = 0;
   out_8244575924748074855[176] = 0;
   out_8244575924748074855[177] = 0;
   out_8244575924748074855[178] = 0;
   out_8244575924748074855[179] = 0;
   out_8244575924748074855[180] = 0;
   out_8244575924748074855[181] = 0;
   out_8244575924748074855[182] = 0;
   out_8244575924748074855[183] = 0;
   out_8244575924748074855[184] = 0;
   out_8244575924748074855[185] = 0;
   out_8244575924748074855[186] = 0;
   out_8244575924748074855[187] = 0;
   out_8244575924748074855[188] = 0;
   out_8244575924748074855[189] = 0;
   out_8244575924748074855[190] = 1;
   out_8244575924748074855[191] = 0;
   out_8244575924748074855[192] = 0;
   out_8244575924748074855[193] = 0;
   out_8244575924748074855[194] = 0;
   out_8244575924748074855[195] = 0;
   out_8244575924748074855[196] = 0;
   out_8244575924748074855[197] = 0;
   out_8244575924748074855[198] = 0;
   out_8244575924748074855[199] = 0;
   out_8244575924748074855[200] = 0;
   out_8244575924748074855[201] = 0;
   out_8244575924748074855[202] = 0;
   out_8244575924748074855[203] = 0;
   out_8244575924748074855[204] = 0;
   out_8244575924748074855[205] = 0;
   out_8244575924748074855[206] = 0;
   out_8244575924748074855[207] = 0;
   out_8244575924748074855[208] = 0;
   out_8244575924748074855[209] = 1;
   out_8244575924748074855[210] = 0;
   out_8244575924748074855[211] = 0;
   out_8244575924748074855[212] = 0;
   out_8244575924748074855[213] = 0;
   out_8244575924748074855[214] = 0;
   out_8244575924748074855[215] = 0;
   out_8244575924748074855[216] = 0;
   out_8244575924748074855[217] = 0;
   out_8244575924748074855[218] = 0;
   out_8244575924748074855[219] = 0;
   out_8244575924748074855[220] = 0;
   out_8244575924748074855[221] = 0;
   out_8244575924748074855[222] = 0;
   out_8244575924748074855[223] = 0;
   out_8244575924748074855[224] = 0;
   out_8244575924748074855[225] = 0;
   out_8244575924748074855[226] = 0;
   out_8244575924748074855[227] = 0;
   out_8244575924748074855[228] = 1;
   out_8244575924748074855[229] = 0;
   out_8244575924748074855[230] = 0;
   out_8244575924748074855[231] = 0;
   out_8244575924748074855[232] = 0;
   out_8244575924748074855[233] = 0;
   out_8244575924748074855[234] = 0;
   out_8244575924748074855[235] = 0;
   out_8244575924748074855[236] = 0;
   out_8244575924748074855[237] = 0;
   out_8244575924748074855[238] = 0;
   out_8244575924748074855[239] = 0;
   out_8244575924748074855[240] = 0;
   out_8244575924748074855[241] = 0;
   out_8244575924748074855[242] = 0;
   out_8244575924748074855[243] = 0;
   out_8244575924748074855[244] = 0;
   out_8244575924748074855[245] = 0;
   out_8244575924748074855[246] = 0;
   out_8244575924748074855[247] = 1;
   out_8244575924748074855[248] = 0;
   out_8244575924748074855[249] = 0;
   out_8244575924748074855[250] = 0;
   out_8244575924748074855[251] = 0;
   out_8244575924748074855[252] = 0;
   out_8244575924748074855[253] = 0;
   out_8244575924748074855[254] = 0;
   out_8244575924748074855[255] = 0;
   out_8244575924748074855[256] = 0;
   out_8244575924748074855[257] = 0;
   out_8244575924748074855[258] = 0;
   out_8244575924748074855[259] = 0;
   out_8244575924748074855[260] = 0;
   out_8244575924748074855[261] = 0;
   out_8244575924748074855[262] = 0;
   out_8244575924748074855[263] = 0;
   out_8244575924748074855[264] = 0;
   out_8244575924748074855[265] = 0;
   out_8244575924748074855[266] = 1;
   out_8244575924748074855[267] = 0;
   out_8244575924748074855[268] = 0;
   out_8244575924748074855[269] = 0;
   out_8244575924748074855[270] = 0;
   out_8244575924748074855[271] = 0;
   out_8244575924748074855[272] = 0;
   out_8244575924748074855[273] = 0;
   out_8244575924748074855[274] = 0;
   out_8244575924748074855[275] = 0;
   out_8244575924748074855[276] = 0;
   out_8244575924748074855[277] = 0;
   out_8244575924748074855[278] = 0;
   out_8244575924748074855[279] = 0;
   out_8244575924748074855[280] = 0;
   out_8244575924748074855[281] = 0;
   out_8244575924748074855[282] = 0;
   out_8244575924748074855[283] = 0;
   out_8244575924748074855[284] = 0;
   out_8244575924748074855[285] = 1;
   out_8244575924748074855[286] = 0;
   out_8244575924748074855[287] = 0;
   out_8244575924748074855[288] = 0;
   out_8244575924748074855[289] = 0;
   out_8244575924748074855[290] = 0;
   out_8244575924748074855[291] = 0;
   out_8244575924748074855[292] = 0;
   out_8244575924748074855[293] = 0;
   out_8244575924748074855[294] = 0;
   out_8244575924748074855[295] = 0;
   out_8244575924748074855[296] = 0;
   out_8244575924748074855[297] = 0;
   out_8244575924748074855[298] = 0;
   out_8244575924748074855[299] = 0;
   out_8244575924748074855[300] = 0;
   out_8244575924748074855[301] = 0;
   out_8244575924748074855[302] = 0;
   out_8244575924748074855[303] = 0;
   out_8244575924748074855[304] = 1;
   out_8244575924748074855[305] = 0;
   out_8244575924748074855[306] = 0;
   out_8244575924748074855[307] = 0;
   out_8244575924748074855[308] = 0;
   out_8244575924748074855[309] = 0;
   out_8244575924748074855[310] = 0;
   out_8244575924748074855[311] = 0;
   out_8244575924748074855[312] = 0;
   out_8244575924748074855[313] = 0;
   out_8244575924748074855[314] = 0;
   out_8244575924748074855[315] = 0;
   out_8244575924748074855[316] = 0;
   out_8244575924748074855[317] = 0;
   out_8244575924748074855[318] = 0;
   out_8244575924748074855[319] = 0;
   out_8244575924748074855[320] = 0;
   out_8244575924748074855[321] = 0;
   out_8244575924748074855[322] = 0;
   out_8244575924748074855[323] = 1;
}
void h_4(double *state, double *unused, double *out_5521956295356383035) {
   out_5521956295356383035[0] = state[6] + state[9];
   out_5521956295356383035[1] = state[7] + state[10];
   out_5521956295356383035[2] = state[8] + state[11];
}
void H_4(double *state, double *unused, double *out_8165506278993683607) {
   out_8165506278993683607[0] = 0;
   out_8165506278993683607[1] = 0;
   out_8165506278993683607[2] = 0;
   out_8165506278993683607[3] = 0;
   out_8165506278993683607[4] = 0;
   out_8165506278993683607[5] = 0;
   out_8165506278993683607[6] = 1;
   out_8165506278993683607[7] = 0;
   out_8165506278993683607[8] = 0;
   out_8165506278993683607[9] = 1;
   out_8165506278993683607[10] = 0;
   out_8165506278993683607[11] = 0;
   out_8165506278993683607[12] = 0;
   out_8165506278993683607[13] = 0;
   out_8165506278993683607[14] = 0;
   out_8165506278993683607[15] = 0;
   out_8165506278993683607[16] = 0;
   out_8165506278993683607[17] = 0;
   out_8165506278993683607[18] = 0;
   out_8165506278993683607[19] = 0;
   out_8165506278993683607[20] = 0;
   out_8165506278993683607[21] = 0;
   out_8165506278993683607[22] = 0;
   out_8165506278993683607[23] = 0;
   out_8165506278993683607[24] = 0;
   out_8165506278993683607[25] = 1;
   out_8165506278993683607[26] = 0;
   out_8165506278993683607[27] = 0;
   out_8165506278993683607[28] = 1;
   out_8165506278993683607[29] = 0;
   out_8165506278993683607[30] = 0;
   out_8165506278993683607[31] = 0;
   out_8165506278993683607[32] = 0;
   out_8165506278993683607[33] = 0;
   out_8165506278993683607[34] = 0;
   out_8165506278993683607[35] = 0;
   out_8165506278993683607[36] = 0;
   out_8165506278993683607[37] = 0;
   out_8165506278993683607[38] = 0;
   out_8165506278993683607[39] = 0;
   out_8165506278993683607[40] = 0;
   out_8165506278993683607[41] = 0;
   out_8165506278993683607[42] = 0;
   out_8165506278993683607[43] = 0;
   out_8165506278993683607[44] = 1;
   out_8165506278993683607[45] = 0;
   out_8165506278993683607[46] = 0;
   out_8165506278993683607[47] = 1;
   out_8165506278993683607[48] = 0;
   out_8165506278993683607[49] = 0;
   out_8165506278993683607[50] = 0;
   out_8165506278993683607[51] = 0;
   out_8165506278993683607[52] = 0;
   out_8165506278993683607[53] = 0;
}
void h_10(double *state, double *unused, double *out_5763131317274676048) {
   out_5763131317274676048[0] = 9.8100000000000005*sin(state[1]) - state[4]*state[8] + state[5]*state[7] + state[12] + state[15];
   out_5763131317274676048[1] = -9.8100000000000005*sin(state[0])*cos(state[1]) + state[3]*state[8] - state[5]*state[6] + state[13] + state[16];
   out_5763131317274676048[2] = -9.8100000000000005*cos(state[0])*cos(state[1]) - state[3]*state[7] + state[4]*state[6] + state[14] + state[17];
}
void H_10(double *state, double *unused, double *out_6718530209189586391) {
   out_6718530209189586391[0] = 0;
   out_6718530209189586391[1] = 9.8100000000000005*cos(state[1]);
   out_6718530209189586391[2] = 0;
   out_6718530209189586391[3] = 0;
   out_6718530209189586391[4] = -state[8];
   out_6718530209189586391[5] = state[7];
   out_6718530209189586391[6] = 0;
   out_6718530209189586391[7] = state[5];
   out_6718530209189586391[8] = -state[4];
   out_6718530209189586391[9] = 0;
   out_6718530209189586391[10] = 0;
   out_6718530209189586391[11] = 0;
   out_6718530209189586391[12] = 1;
   out_6718530209189586391[13] = 0;
   out_6718530209189586391[14] = 0;
   out_6718530209189586391[15] = 1;
   out_6718530209189586391[16] = 0;
   out_6718530209189586391[17] = 0;
   out_6718530209189586391[18] = -9.8100000000000005*cos(state[0])*cos(state[1]);
   out_6718530209189586391[19] = 9.8100000000000005*sin(state[0])*sin(state[1]);
   out_6718530209189586391[20] = 0;
   out_6718530209189586391[21] = state[8];
   out_6718530209189586391[22] = 0;
   out_6718530209189586391[23] = -state[6];
   out_6718530209189586391[24] = -state[5];
   out_6718530209189586391[25] = 0;
   out_6718530209189586391[26] = state[3];
   out_6718530209189586391[27] = 0;
   out_6718530209189586391[28] = 0;
   out_6718530209189586391[29] = 0;
   out_6718530209189586391[30] = 0;
   out_6718530209189586391[31] = 1;
   out_6718530209189586391[32] = 0;
   out_6718530209189586391[33] = 0;
   out_6718530209189586391[34] = 1;
   out_6718530209189586391[35] = 0;
   out_6718530209189586391[36] = 9.8100000000000005*sin(state[0])*cos(state[1]);
   out_6718530209189586391[37] = 9.8100000000000005*sin(state[1])*cos(state[0]);
   out_6718530209189586391[38] = 0;
   out_6718530209189586391[39] = -state[7];
   out_6718530209189586391[40] = state[6];
   out_6718530209189586391[41] = 0;
   out_6718530209189586391[42] = state[4];
   out_6718530209189586391[43] = -state[3];
   out_6718530209189586391[44] = 0;
   out_6718530209189586391[45] = 0;
   out_6718530209189586391[46] = 0;
   out_6718530209189586391[47] = 0;
   out_6718530209189586391[48] = 0;
   out_6718530209189586391[49] = 0;
   out_6718530209189586391[50] = 1;
   out_6718530209189586391[51] = 0;
   out_6718530209189586391[52] = 0;
   out_6718530209189586391[53] = 1;
}
void h_13(double *state, double *unused, double *out_5096590534574108672) {
   out_5096590534574108672[0] = state[3];
   out_5096590534574108672[1] = state[4];
   out_5096590534574108672[2] = state[5];
}
void H_13(double *state, double *unused, double *out_7068963969383535208) {
   out_7068963969383535208[0] = 0;
   out_7068963969383535208[1] = 0;
   out_7068963969383535208[2] = 0;
   out_7068963969383535208[3] = 1;
   out_7068963969383535208[4] = 0;
   out_7068963969383535208[5] = 0;
   out_7068963969383535208[6] = 0;
   out_7068963969383535208[7] = 0;
   out_7068963969383535208[8] = 0;
   out_7068963969383535208[9] = 0;
   out_7068963969383535208[10] = 0;
   out_7068963969383535208[11] = 0;
   out_7068963969383535208[12] = 0;
   out_7068963969383535208[13] = 0;
   out_7068963969383535208[14] = 0;
   out_7068963969383535208[15] = 0;
   out_7068963969383535208[16] = 0;
   out_7068963969383535208[17] = 0;
   out_7068963969383535208[18] = 0;
   out_7068963969383535208[19] = 0;
   out_7068963969383535208[20] = 0;
   out_7068963969383535208[21] = 0;
   out_7068963969383535208[22] = 1;
   out_7068963969383535208[23] = 0;
   out_7068963969383535208[24] = 0;
   out_7068963969383535208[25] = 0;
   out_7068963969383535208[26] = 0;
   out_7068963969383535208[27] = 0;
   out_7068963969383535208[28] = 0;
   out_7068963969383535208[29] = 0;
   out_7068963969383535208[30] = 0;
   out_7068963969383535208[31] = 0;
   out_7068963969383535208[32] = 0;
   out_7068963969383535208[33] = 0;
   out_7068963969383535208[34] = 0;
   out_7068963969383535208[35] = 0;
   out_7068963969383535208[36] = 0;
   out_7068963969383535208[37] = 0;
   out_7068963969383535208[38] = 0;
   out_7068963969383535208[39] = 0;
   out_7068963969383535208[40] = 0;
   out_7068963969383535208[41] = 1;
   out_7068963969383535208[42] = 0;
   out_7068963969383535208[43] = 0;
   out_7068963969383535208[44] = 0;
   out_7068963969383535208[45] = 0;
   out_7068963969383535208[46] = 0;
   out_7068963969383535208[47] = 0;
   out_7068963969383535208[48] = 0;
   out_7068963969383535208[49] = 0;
   out_7068963969383535208[50] = 0;
   out_7068963969383535208[51] = 0;
   out_7068963969383535208[52] = 0;
   out_7068963969383535208[53] = 0;
}
void h_14(double *state, double *unused, double *out_2487350392839388599) {
   out_2487350392839388599[0] = state[6];
   out_2487350392839388599[1] = state[7];
   out_2487350392839388599[2] = state[8];
}
void H_14(double *state, double *unused, double *out_6317996938376383480) {
   out_6317996938376383480[0] = 0;
   out_6317996938376383480[1] = 0;
   out_6317996938376383480[2] = 0;
   out_6317996938376383480[3] = 0;
   out_6317996938376383480[4] = 0;
   out_6317996938376383480[5] = 0;
   out_6317996938376383480[6] = 1;
   out_6317996938376383480[7] = 0;
   out_6317996938376383480[8] = 0;
   out_6317996938376383480[9] = 0;
   out_6317996938376383480[10] = 0;
   out_6317996938376383480[11] = 0;
   out_6317996938376383480[12] = 0;
   out_6317996938376383480[13] = 0;
   out_6317996938376383480[14] = 0;
   out_6317996938376383480[15] = 0;
   out_6317996938376383480[16] = 0;
   out_6317996938376383480[17] = 0;
   out_6317996938376383480[18] = 0;
   out_6317996938376383480[19] = 0;
   out_6317996938376383480[20] = 0;
   out_6317996938376383480[21] = 0;
   out_6317996938376383480[22] = 0;
   out_6317996938376383480[23] = 0;
   out_6317996938376383480[24] = 0;
   out_6317996938376383480[25] = 1;
   out_6317996938376383480[26] = 0;
   out_6317996938376383480[27] = 0;
   out_6317996938376383480[28] = 0;
   out_6317996938376383480[29] = 0;
   out_6317996938376383480[30] = 0;
   out_6317996938376383480[31] = 0;
   out_6317996938376383480[32] = 0;
   out_6317996938376383480[33] = 0;
   out_6317996938376383480[34] = 0;
   out_6317996938376383480[35] = 0;
   out_6317996938376383480[36] = 0;
   out_6317996938376383480[37] = 0;
   out_6317996938376383480[38] = 0;
   out_6317996938376383480[39] = 0;
   out_6317996938376383480[40] = 0;
   out_6317996938376383480[41] = 0;
   out_6317996938376383480[42] = 0;
   out_6317996938376383480[43] = 0;
   out_6317996938376383480[44] = 1;
   out_6317996938376383480[45] = 0;
   out_6317996938376383480[46] = 0;
   out_6317996938376383480[47] = 0;
   out_6317996938376383480[48] = 0;
   out_6317996938376383480[49] = 0;
   out_6317996938376383480[50] = 0;
   out_6317996938376383480[51] = 0;
   out_6317996938376383480[52] = 0;
   out_6317996938376383480[53] = 0;
}
#include <eigen3/Eigen/Dense>
#include <iostream>

typedef Eigen::Matrix<double, DIM, DIM, Eigen::RowMajor> DDM;
typedef Eigen::Matrix<double, EDIM, EDIM, Eigen::RowMajor> EEM;
typedef Eigen::Matrix<double, DIM, EDIM, Eigen::RowMajor> DEM;

void predict(double *in_x, double *in_P, double *in_Q, double dt) {
  typedef Eigen::Matrix<double, MEDIM, MEDIM, Eigen::RowMajor> RRM;

  double nx[DIM] = {0};
  double in_F[EDIM*EDIM] = {0};

  // functions from sympy
  f_fun(in_x, dt, nx);
  F_fun(in_x, dt, in_F);


  EEM F(in_F);
  EEM P(in_P);
  EEM Q(in_Q);

  RRM F_main = F.topLeftCorner(MEDIM, MEDIM);
  P.topLeftCorner(MEDIM, MEDIM) = (F_main * P.topLeftCorner(MEDIM, MEDIM)) * F_main.transpose();
  P.topRightCorner(MEDIM, EDIM - MEDIM) = F_main * P.topRightCorner(MEDIM, EDIM - MEDIM);
  P.bottomLeftCorner(EDIM - MEDIM, MEDIM) = P.bottomLeftCorner(EDIM - MEDIM, MEDIM) * F_main.transpose();

  P = P + dt*Q;

  // copy out state
  memcpy(in_x, nx, DIM * sizeof(double));
  memcpy(in_P, P.data(), EDIM * EDIM * sizeof(double));
}

// note: extra_args dim only correct when null space projecting
// otherwise 1
template <int ZDIM, int EADIM, bool MAHA_TEST>
void update(double *in_x, double *in_P, Hfun h_fun, Hfun H_fun, Hfun Hea_fun, double *in_z, double *in_R, double *in_ea, double MAHA_THRESHOLD) {
  typedef Eigen::Matrix<double, ZDIM, ZDIM, Eigen::RowMajor> ZZM;
  typedef Eigen::Matrix<double, ZDIM, DIM, Eigen::RowMajor> ZDM;
  typedef Eigen::Matrix<double, Eigen::Dynamic, EDIM, Eigen::RowMajor> XEM;
  //typedef Eigen::Matrix<double, EDIM, ZDIM, Eigen::RowMajor> EZM;
  typedef Eigen::Matrix<double, Eigen::Dynamic, 1> X1M;
  typedef Eigen::Matrix<double, Eigen::Dynamic, Eigen::Dynamic, Eigen::RowMajor> XXM;

  double in_hx[ZDIM] = {0};
  double in_H[ZDIM * DIM] = {0};
  double in_H_mod[EDIM * DIM] = {0};
  double delta_x[EDIM] = {0};
  double x_new[DIM] = {0};


  // state x, P
  Eigen::Matrix<double, ZDIM, 1> z(in_z);
  EEM P(in_P);
  ZZM pre_R(in_R);

  // functions from sympy
  h_fun(in_x, in_ea, in_hx);
  H_fun(in_x, in_ea, in_H);
  ZDM pre_H(in_H);

  // get y (y = z - hx)
  Eigen::Matrix<double, ZDIM, 1> pre_y(in_hx); pre_y = z - pre_y;
  X1M y; XXM H; XXM R;
  if (Hea_fun){
    typedef Eigen::Matrix<double, ZDIM, EADIM, Eigen::RowMajor> ZAM;
    double in_Hea[ZDIM * EADIM] = {0};
    Hea_fun(in_x, in_ea, in_Hea);
    ZAM Hea(in_Hea);
    XXM A = Hea.transpose().fullPivLu().kernel();


    y = A.transpose() * pre_y;
    H = A.transpose() * pre_H;
    R = A.transpose() * pre_R * A;
  } else {
    y = pre_y;
    H = pre_H;
    R = pre_R;
  }
  // get modified H
  H_mod_fun(in_x, in_H_mod);
  DEM H_mod(in_H_mod);
  XEM H_err = H * H_mod;

  // Do mahalobis distance test
  if (MAHA_TEST){
    XXM a = (H_err * P * H_err.transpose() + R).inverse();
    double maha_dist = y.transpose() * a * y;
    if (maha_dist > MAHA_THRESHOLD){
      R = 1.0e16 * R;
    }
  }

  // Outlier resilient weighting
  double weight = 1;//(1.5)/(1 + y.squaredNorm()/R.sum());

  // kalman gains and I_KH
  XXM S = ((H_err * P) * H_err.transpose()) + R/weight;
  XEM KT = S.fullPivLu().solve(H_err * P.transpose());
  //EZM K = KT.transpose(); TODO: WHY DOES THIS NOT COMPILE?
  //EZM K = S.fullPivLu().solve(H_err * P.transpose()).transpose();
  //std::cout << "Here is the matrix rot:\n" << K << std::endl;
  EEM I_KH = Eigen::Matrix<double, EDIM, EDIM>::Identity() - (KT.transpose() * H_err);

  // update state by injecting dx
  Eigen::Matrix<double, EDIM, 1> dx(delta_x);
  dx  = (KT.transpose() * y);
  memcpy(delta_x, dx.data(), EDIM * sizeof(double));
  err_fun(in_x, delta_x, x_new);
  Eigen::Matrix<double, DIM, 1> x(x_new);

  // update cov
  P = ((I_KH * P) * I_KH.transpose()) + ((KT.transpose() * R) * KT);

  // copy out state
  memcpy(in_x, x.data(), DIM * sizeof(double));
  memcpy(in_P, P.data(), EDIM * EDIM * sizeof(double));
  memcpy(in_z, y.data(), y.rows() * sizeof(double));
}




}
extern "C" {

void pose_update_4(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea) {
  update<3, 3, 0>(in_x, in_P, h_4, H_4, NULL, in_z, in_R, in_ea, MAHA_THRESH_4);
}
void pose_update_10(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea) {
  update<3, 3, 0>(in_x, in_P, h_10, H_10, NULL, in_z, in_R, in_ea, MAHA_THRESH_10);
}
void pose_update_13(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea) {
  update<3, 3, 0>(in_x, in_P, h_13, H_13, NULL, in_z, in_R, in_ea, MAHA_THRESH_13);
}
void pose_update_14(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea) {
  update<3, 3, 0>(in_x, in_P, h_14, H_14, NULL, in_z, in_R, in_ea, MAHA_THRESH_14);
}
void pose_err_fun(double *nom_x, double *delta_x, double *out_5785056017088383392) {
  err_fun(nom_x, delta_x, out_5785056017088383392);
}
void pose_inv_err_fun(double *nom_x, double *true_x, double *out_3431901073752666570) {
  inv_err_fun(nom_x, true_x, out_3431901073752666570);
}
void pose_H_mod_fun(double *state, double *out_4433155987963909288) {
  H_mod_fun(state, out_4433155987963909288);
}
void pose_f_fun(double *state, double dt, double *out_6368947249978212614) {
  f_fun(state,  dt, out_6368947249978212614);
}
void pose_F_fun(double *state, double dt, double *out_8244575924748074855) {
  F_fun(state,  dt, out_8244575924748074855);
}
void pose_h_4(double *state, double *unused, double *out_5521956295356383035) {
  h_4(state, unused, out_5521956295356383035);
}
void pose_H_4(double *state, double *unused, double *out_8165506278993683607) {
  H_4(state, unused, out_8165506278993683607);
}
void pose_h_10(double *state, double *unused, double *out_5763131317274676048) {
  h_10(state, unused, out_5763131317274676048);
}
void pose_H_10(double *state, double *unused, double *out_6718530209189586391) {
  H_10(state, unused, out_6718530209189586391);
}
void pose_h_13(double *state, double *unused, double *out_5096590534574108672) {
  h_13(state, unused, out_5096590534574108672);
}
void pose_H_13(double *state, double *unused, double *out_7068963969383535208) {
  H_13(state, unused, out_7068963969383535208);
}
void pose_h_14(double *state, double *unused, double *out_2487350392839388599) {
  h_14(state, unused, out_2487350392839388599);
}
void pose_H_14(double *state, double *unused, double *out_6317996938376383480) {
  H_14(state, unused, out_6317996938376383480);
}
void pose_predict(double *in_x, double *in_P, double *in_Q, double dt) {
  predict(in_x, in_P, in_Q, dt);
}
}

const EKF pose = {
  .name = "pose",
  .kinds = { 4, 10, 13, 14 },
  .feature_kinds = {  },
  .f_fun = pose_f_fun,
  .F_fun = pose_F_fun,
  .err_fun = pose_err_fun,
  .inv_err_fun = pose_inv_err_fun,
  .H_mod_fun = pose_H_mod_fun,
  .predict = pose_predict,
  .hs = {
    { 4, pose_h_4 },
    { 10, pose_h_10 },
    { 13, pose_h_13 },
    { 14, pose_h_14 },
  },
  .Hs = {
    { 4, pose_H_4 },
    { 10, pose_H_10 },
    { 13, pose_H_13 },
    { 14, pose_H_14 },
  },
  .updates = {
    { 4, pose_update_4 },
    { 10, pose_update_10 },
    { 13, pose_update_13 },
    { 14, pose_update_14 },
  },
  .Hes = {
  },
  .sets = {
  },
  .extra_routines = {
  },
};

ekf_lib_init(pose)
