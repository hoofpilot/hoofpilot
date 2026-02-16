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
void car_err_fun(double *nom_x, double *delta_x, double *out_1594150801698997641);
void car_inv_err_fun(double *nom_x, double *true_x, double *out_3157223694652086945);
void car_H_mod_fun(double *state, double *out_501980518016513048);
void car_f_fun(double *state, double dt, double *out_3562028931429149250);
void car_F_fun(double *state, double dt, double *out_4547236169721199402);
void car_h_25(double *state, double *unused, double *out_2473458555518716086);
void car_H_25(double *state, double *unused, double *out_2649139455293893460);
void car_h_24(double *state, double *unused, double *out_5544228173403561954);
void car_H_24(double *state, double *unused, double *out_4005066002814292297);
void car_h_30(double *state, double *unused, double *out_8080346023306312171);
void car_H_30(double *state, double *unused, double *out_7176835785421501658);
void car_h_26(double *state, double *unused, double *out_7329611998958906760);
void car_H_26(double *state, double *unused, double *out_6390642774167949684);
void car_h_27(double *state, double *unused, double *out_3416968408420378521);
void car_H_27(double *state, double *unused, double *out_9095144976487625047);
void car_h_29(double *state, double *unused, double *out_5968445969121610433);
void car_H_29(double *state, double *unused, double *out_6666604441107109474);
void car_h_28(double *state, double *unused, double *out_6453754459864711206);
void car_H_28(double *state, double *unused, double *out_6697740615532911568);
void car_h_31(double *state, double *unused, double *out_2748652617803221975);
void car_H_31(double *state, double *unused, double *out_7016850876401301160);
void car_predict(double *in_x, double *in_P, double *in_Q, double dt);
void car_set_mass(double x);
void car_set_rotational_inertia(double x);
void car_set_center_to_front(double x);
void car_set_center_to_rear(double x);
void car_set_stiffness_front(double x);
void car_set_stiffness_rear(double x);
}