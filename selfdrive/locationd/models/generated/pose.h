#pragma once
#include "rednose/helpers/ekf.h"
extern "C" {
void pose_update_4(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_10(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_13(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_14(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_err_fun(double *nom_x, double *delta_x, double *out_5785056017088383392);
void pose_inv_err_fun(double *nom_x, double *true_x, double *out_3431901073752666570);
void pose_H_mod_fun(double *state, double *out_4433155987963909288);
void pose_f_fun(double *state, double dt, double *out_6368947249978212614);
void pose_F_fun(double *state, double dt, double *out_8244575924748074855);
void pose_h_4(double *state, double *unused, double *out_5521956295356383035);
void pose_H_4(double *state, double *unused, double *out_8165506278993683607);
void pose_h_10(double *state, double *unused, double *out_5763131317274676048);
void pose_H_10(double *state, double *unused, double *out_6718530209189586391);
void pose_h_13(double *state, double *unused, double *out_5096590534574108672);
void pose_H_13(double *state, double *unused, double *out_7068963969383535208);
void pose_h_14(double *state, double *unused, double *out_2487350392839388599);
void pose_H_14(double *state, double *unused, double *out_6317996938376383480);
void pose_predict(double *in_x, double *in_P, double *in_Q, double dt);
}