#pragma once
#include "rednose/helpers/ekf.h"
extern "C" {
void live_update_4(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void live_update_9(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void live_update_10(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void live_update_12(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void live_update_35(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void live_update_32(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void live_update_13(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void live_update_14(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void live_update_33(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void live_H(double *in_vec, double *out_5962897977967004088);
void live_err_fun(double *nom_x, double *delta_x, double *out_3380898399318836457);
void live_inv_err_fun(double *nom_x, double *true_x, double *out_310135518597333084);
void live_H_mod_fun(double *state, double *out_11707341081037286);
void live_f_fun(double *state, double dt, double *out_720455311092864950);
void live_F_fun(double *state, double dt, double *out_147573761717917967);
void live_h_4(double *state, double *unused, double *out_2938391147935515206);
void live_H_4(double *state, double *unused, double *out_5507114147673910411);
void live_h_9(double *state, double *unused, double *out_6037744850673500043);
void live_H_9(double *state, double *unused, double *out_5265924501044319766);
void live_h_10(double *state, double *unused, double *out_5425196116025649875);
void live_H_10(double *state, double *unused, double *out_7263810002127032168);
void live_h_12(double *state, double *unused, double *out_2547918808482388431);
void live_H_12(double *state, double *unused, double *out_487657739641948616);
void live_h_35(double *state, double *unused, double *out_4097824800937556461);
void live_H_35(double *state, double *unused, double *out_2140452090301303035);
void live_h_32(double *state, double *unused, double *out_5696219884119238162);
void live_H_32(double *state, double *unused, double *out_3660852281906309523);
void live_h_13(double *state, double *unused, double *out_2741274553588607265);
void live_H_13(double *state, double *unused, double *out_1796329621365762794);
void live_h_14(double *state, double *unused, double *out_6037744850673500043);
void live_H_14(double *state, double *unused, double *out_5265924501044319766);
void live_h_33(double *state, double *unused, double *out_3576740732811430980);
void live_H_33(double *state, double *unused, double *out_1010104914337554569);
void live_predict(double *in_x, double *in_P, double *in_Q, double dt);
}