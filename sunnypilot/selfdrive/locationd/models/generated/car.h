#pragma once
#include "rednose/helpers/ekf.h"
extern "C" {
void car_update_25(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void car_update_24(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void car_update_30(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void car_update_26(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void car_update_27(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void car_update_29(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void car_update_28(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void car_update_31(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void car_err_fun(double *nom_x, double *delta_x, double *out_4802421531557453693);
void car_inv_err_fun(double *nom_x, double *true_x, double *out_4533876151458390791);
void car_H_mod_fun(double *state, double *out_2305283590885064726);
void car_f_fun(double *state, double dt, double *out_6813101336163725268);
void car_F_fun(double *state, double dt, double *out_1339072285061349588);
void car_h_25(double *state, double *unused, double *out_9061235835578842003);
void car_H_25(double *state, double *unused, double *out_7208975416069729566);
void car_h_24(double *state, double *unused, double *out_5781965406962125422);
void car_H_24(double *state, double *unused, double *out_9060554234032672077);
void car_h_30(double *state, double *unused, double *out_8904049167227712858);
void car_H_30(double *state, double *unused, double *out_8719435699132573423);
void car_h_26(double *state, double *unused, double *out_6922026533145213466);
void car_H_26(double *state, double *unused, double *out_3467472097195673342);
void car_h_27(double *state, double *unused, double *out_8391331842468009564);
void car_H_27(double *state, double *unused, double *out_7552545062776553282);
void car_h_29(double *state, double *unused, double *out_6299643846419015207);
void car_H_29(double *state, double *unused, double *out_8209204354818181239);
void car_h_28(double *state, double *unused, double *out_539365752793676863);
void car_H_28(double *state, double *unused, double *out_5155140701821839803);
void car_h_31(double *state, double *unused, double *out_1924949473881821288);
void car_H_31(double *state, double *unused, double *out_2841263994962321866);
void car_predict(double *in_x, double *in_P, double *in_Q, double dt);
void car_set_mass(double x);
void car_set_rotational_inertia(double x);
void car_set_center_to_front(double x);
void car_set_center_to_rear(double x);
void car_set_stiffness_front(double x);
void car_set_stiffness_rear(double x);
}