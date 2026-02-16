#include "car.h"

namespace {
#define DIM 9
#define EDIM 9
#define MEDIM 9
typedef void (*Hfun)(double *, double *, double *);

double mass;

void set_mass(double x){ mass = x;}

double rotational_inertia;

void set_rotational_inertia(double x){ rotational_inertia = x;}

double center_to_front;

void set_center_to_front(double x){ center_to_front = x;}

double center_to_rear;

void set_center_to_rear(double x){ center_to_rear = x;}

double stiffness_front;

void set_stiffness_front(double x){ stiffness_front = x;}

double stiffness_rear;

void set_stiffness_rear(double x){ stiffness_rear = x;}
const static double MAHA_THRESH_25 = 3.8414588206941227;
const static double MAHA_THRESH_24 = 5.991464547107981;
const static double MAHA_THRESH_30 = 3.8414588206941227;
const static double MAHA_THRESH_26 = 3.8414588206941227;
const static double MAHA_THRESH_27 = 3.8414588206941227;
const static double MAHA_THRESH_29 = 3.8414588206941227;
const static double MAHA_THRESH_28 = 3.8414588206941227;
const static double MAHA_THRESH_31 = 3.8414588206941227;

/******************************************************************************
 *                      Code generated with SymPy 1.14.0                      *
 *                                                                            *
 *              See http://www.sympy.org/ for more information.               *
 *                                                                            *
 *                         This file is part of 'ekf'                         *
 ******************************************************************************/
void err_fun(double *nom_x, double *delta_x, double *out_1594150801698997641) {
   out_1594150801698997641[0] = delta_x[0] + nom_x[0];
   out_1594150801698997641[1] = delta_x[1] + nom_x[1];
   out_1594150801698997641[2] = delta_x[2] + nom_x[2];
   out_1594150801698997641[3] = delta_x[3] + nom_x[3];
   out_1594150801698997641[4] = delta_x[4] + nom_x[4];
   out_1594150801698997641[5] = delta_x[5] + nom_x[5];
   out_1594150801698997641[6] = delta_x[6] + nom_x[6];
   out_1594150801698997641[7] = delta_x[7] + nom_x[7];
   out_1594150801698997641[8] = delta_x[8] + nom_x[8];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_3157223694652086945) {
   out_3157223694652086945[0] = -nom_x[0] + true_x[0];
   out_3157223694652086945[1] = -nom_x[1] + true_x[1];
   out_3157223694652086945[2] = -nom_x[2] + true_x[2];
   out_3157223694652086945[3] = -nom_x[3] + true_x[3];
   out_3157223694652086945[4] = -nom_x[4] + true_x[4];
   out_3157223694652086945[5] = -nom_x[5] + true_x[5];
   out_3157223694652086945[6] = -nom_x[6] + true_x[6];
   out_3157223694652086945[7] = -nom_x[7] + true_x[7];
   out_3157223694652086945[8] = -nom_x[8] + true_x[8];
}
void H_mod_fun(double *state, double *out_501980518016513048) {
   out_501980518016513048[0] = 1.0;
   out_501980518016513048[1] = 0.0;
   out_501980518016513048[2] = 0.0;
   out_501980518016513048[3] = 0.0;
   out_501980518016513048[4] = 0.0;
   out_501980518016513048[5] = 0.0;
   out_501980518016513048[6] = 0.0;
   out_501980518016513048[7] = 0.0;
   out_501980518016513048[8] = 0.0;
   out_501980518016513048[9] = 0.0;
   out_501980518016513048[10] = 1.0;
   out_501980518016513048[11] = 0.0;
   out_501980518016513048[12] = 0.0;
   out_501980518016513048[13] = 0.0;
   out_501980518016513048[14] = 0.0;
   out_501980518016513048[15] = 0.0;
   out_501980518016513048[16] = 0.0;
   out_501980518016513048[17] = 0.0;
   out_501980518016513048[18] = 0.0;
   out_501980518016513048[19] = 0.0;
   out_501980518016513048[20] = 1.0;
   out_501980518016513048[21] = 0.0;
   out_501980518016513048[22] = 0.0;
   out_501980518016513048[23] = 0.0;
   out_501980518016513048[24] = 0.0;
   out_501980518016513048[25] = 0.0;
   out_501980518016513048[26] = 0.0;
   out_501980518016513048[27] = 0.0;
   out_501980518016513048[28] = 0.0;
   out_501980518016513048[29] = 0.0;
   out_501980518016513048[30] = 1.0;
   out_501980518016513048[31] = 0.0;
   out_501980518016513048[32] = 0.0;
   out_501980518016513048[33] = 0.0;
   out_501980518016513048[34] = 0.0;
   out_501980518016513048[35] = 0.0;
   out_501980518016513048[36] = 0.0;
   out_501980518016513048[37] = 0.0;
   out_501980518016513048[38] = 0.0;
   out_501980518016513048[39] = 0.0;
   out_501980518016513048[40] = 1.0;
   out_501980518016513048[41] = 0.0;
   out_501980518016513048[42] = 0.0;
   out_501980518016513048[43] = 0.0;
   out_501980518016513048[44] = 0.0;
   out_501980518016513048[45] = 0.0;
   out_501980518016513048[46] = 0.0;
   out_501980518016513048[47] = 0.0;
   out_501980518016513048[48] = 0.0;
   out_501980518016513048[49] = 0.0;
   out_501980518016513048[50] = 1.0;
   out_501980518016513048[51] = 0.0;
   out_501980518016513048[52] = 0.0;
   out_501980518016513048[53] = 0.0;
   out_501980518016513048[54] = 0.0;
   out_501980518016513048[55] = 0.0;
   out_501980518016513048[56] = 0.0;
   out_501980518016513048[57] = 0.0;
   out_501980518016513048[58] = 0.0;
   out_501980518016513048[59] = 0.0;
   out_501980518016513048[60] = 1.0;
   out_501980518016513048[61] = 0.0;
   out_501980518016513048[62] = 0.0;
   out_501980518016513048[63] = 0.0;
   out_501980518016513048[64] = 0.0;
   out_501980518016513048[65] = 0.0;
   out_501980518016513048[66] = 0.0;
   out_501980518016513048[67] = 0.0;
   out_501980518016513048[68] = 0.0;
   out_501980518016513048[69] = 0.0;
   out_501980518016513048[70] = 1.0;
   out_501980518016513048[71] = 0.0;
   out_501980518016513048[72] = 0.0;
   out_501980518016513048[73] = 0.0;
   out_501980518016513048[74] = 0.0;
   out_501980518016513048[75] = 0.0;
   out_501980518016513048[76] = 0.0;
   out_501980518016513048[77] = 0.0;
   out_501980518016513048[78] = 0.0;
   out_501980518016513048[79] = 0.0;
   out_501980518016513048[80] = 1.0;
}
void f_fun(double *state, double dt, double *out_3562028931429149250) {
   out_3562028931429149250[0] = state[0];
   out_3562028931429149250[1] = state[1];
   out_3562028931429149250[2] = state[2];
   out_3562028931429149250[3] = state[3];
   out_3562028931429149250[4] = state[4];
   out_3562028931429149250[5] = dt*((-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]))*state[6] - 9.8100000000000005*state[8] + stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*state[1]) + (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*state[4])) + state[5];
   out_3562028931429149250[6] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*state[4])) + state[6];
   out_3562028931429149250[7] = state[7];
   out_3562028931429149250[8] = state[8];
}
void F_fun(double *state, double dt, double *out_4547236169721199402) {
   out_4547236169721199402[0] = 1;
   out_4547236169721199402[1] = 0;
   out_4547236169721199402[2] = 0;
   out_4547236169721199402[3] = 0;
   out_4547236169721199402[4] = 0;
   out_4547236169721199402[5] = 0;
   out_4547236169721199402[6] = 0;
   out_4547236169721199402[7] = 0;
   out_4547236169721199402[8] = 0;
   out_4547236169721199402[9] = 0;
   out_4547236169721199402[10] = 1;
   out_4547236169721199402[11] = 0;
   out_4547236169721199402[12] = 0;
   out_4547236169721199402[13] = 0;
   out_4547236169721199402[14] = 0;
   out_4547236169721199402[15] = 0;
   out_4547236169721199402[16] = 0;
   out_4547236169721199402[17] = 0;
   out_4547236169721199402[18] = 0;
   out_4547236169721199402[19] = 0;
   out_4547236169721199402[20] = 1;
   out_4547236169721199402[21] = 0;
   out_4547236169721199402[22] = 0;
   out_4547236169721199402[23] = 0;
   out_4547236169721199402[24] = 0;
   out_4547236169721199402[25] = 0;
   out_4547236169721199402[26] = 0;
   out_4547236169721199402[27] = 0;
   out_4547236169721199402[28] = 0;
   out_4547236169721199402[29] = 0;
   out_4547236169721199402[30] = 1;
   out_4547236169721199402[31] = 0;
   out_4547236169721199402[32] = 0;
   out_4547236169721199402[33] = 0;
   out_4547236169721199402[34] = 0;
   out_4547236169721199402[35] = 0;
   out_4547236169721199402[36] = 0;
   out_4547236169721199402[37] = 0;
   out_4547236169721199402[38] = 0;
   out_4547236169721199402[39] = 0;
   out_4547236169721199402[40] = 1;
   out_4547236169721199402[41] = 0;
   out_4547236169721199402[42] = 0;
   out_4547236169721199402[43] = 0;
   out_4547236169721199402[44] = 0;
   out_4547236169721199402[45] = dt*(stiffness_front*(-state[2] - state[3] + state[7])/(mass*state[1]) + (-stiffness_front - stiffness_rear)*state[5]/(mass*state[4]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[6]/(mass*state[4]));
   out_4547236169721199402[46] = -dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*pow(state[1], 2));
   out_4547236169721199402[47] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_4547236169721199402[48] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_4547236169721199402[49] = dt*((-1 - (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*pow(state[4], 2)))*state[6] - (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*pow(state[4], 2)));
   out_4547236169721199402[50] = dt*(-stiffness_front*state[0] - stiffness_rear*state[0])/(mass*state[4]) + 1;
   out_4547236169721199402[51] = dt*(-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]));
   out_4547236169721199402[52] = dt*stiffness_front*state[0]/(mass*state[1]);
   out_4547236169721199402[53] = -9.8100000000000005*dt;
   out_4547236169721199402[54] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front - pow(center_to_rear, 2)*stiffness_rear)*state[6]/(rotational_inertia*state[4]));
   out_4547236169721199402[55] = -center_to_front*dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*pow(state[1], 2));
   out_4547236169721199402[56] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_4547236169721199402[57] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_4547236169721199402[58] = dt*(-(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*pow(state[4], 2)) - (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*pow(state[4], 2)));
   out_4547236169721199402[59] = dt*(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(rotational_inertia*state[4]);
   out_4547236169721199402[60] = dt*(-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])/(rotational_inertia*state[4]) + 1;
   out_4547236169721199402[61] = center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_4547236169721199402[62] = 0;
   out_4547236169721199402[63] = 0;
   out_4547236169721199402[64] = 0;
   out_4547236169721199402[65] = 0;
   out_4547236169721199402[66] = 0;
   out_4547236169721199402[67] = 0;
   out_4547236169721199402[68] = 0;
   out_4547236169721199402[69] = 0;
   out_4547236169721199402[70] = 1;
   out_4547236169721199402[71] = 0;
   out_4547236169721199402[72] = 0;
   out_4547236169721199402[73] = 0;
   out_4547236169721199402[74] = 0;
   out_4547236169721199402[75] = 0;
   out_4547236169721199402[76] = 0;
   out_4547236169721199402[77] = 0;
   out_4547236169721199402[78] = 0;
   out_4547236169721199402[79] = 0;
   out_4547236169721199402[80] = 1;
}
void h_25(double *state, double *unused, double *out_2473458555518716086) {
   out_2473458555518716086[0] = state[6];
}
void H_25(double *state, double *unused, double *out_2649139455293893460) {
   out_2649139455293893460[0] = 0;
   out_2649139455293893460[1] = 0;
   out_2649139455293893460[2] = 0;
   out_2649139455293893460[3] = 0;
   out_2649139455293893460[4] = 0;
   out_2649139455293893460[5] = 0;
   out_2649139455293893460[6] = 1;
   out_2649139455293893460[7] = 0;
   out_2649139455293893460[8] = 0;
}
void h_24(double *state, double *unused, double *out_5544228173403561954) {
   out_5544228173403561954[0] = state[4];
   out_5544228173403561954[1] = state[5];
}
void H_24(double *state, double *unused, double *out_4005066002814292297) {
   out_4005066002814292297[0] = 0;
   out_4005066002814292297[1] = 0;
   out_4005066002814292297[2] = 0;
   out_4005066002814292297[3] = 0;
   out_4005066002814292297[4] = 1;
   out_4005066002814292297[5] = 0;
   out_4005066002814292297[6] = 0;
   out_4005066002814292297[7] = 0;
   out_4005066002814292297[8] = 0;
   out_4005066002814292297[9] = 0;
   out_4005066002814292297[10] = 0;
   out_4005066002814292297[11] = 0;
   out_4005066002814292297[12] = 0;
   out_4005066002814292297[13] = 0;
   out_4005066002814292297[14] = 1;
   out_4005066002814292297[15] = 0;
   out_4005066002814292297[16] = 0;
   out_4005066002814292297[17] = 0;
}
void h_30(double *state, double *unused, double *out_8080346023306312171) {
   out_8080346023306312171[0] = state[4];
}
void H_30(double *state, double *unused, double *out_7176835785421501658) {
   out_7176835785421501658[0] = 0;
   out_7176835785421501658[1] = 0;
   out_7176835785421501658[2] = 0;
   out_7176835785421501658[3] = 0;
   out_7176835785421501658[4] = 1;
   out_7176835785421501658[5] = 0;
   out_7176835785421501658[6] = 0;
   out_7176835785421501658[7] = 0;
   out_7176835785421501658[8] = 0;
}
void h_26(double *state, double *unused, double *out_7329611998958906760) {
   out_7329611998958906760[0] = state[7];
}
void H_26(double *state, double *unused, double *out_6390642774167949684) {
   out_6390642774167949684[0] = 0;
   out_6390642774167949684[1] = 0;
   out_6390642774167949684[2] = 0;
   out_6390642774167949684[3] = 0;
   out_6390642774167949684[4] = 0;
   out_6390642774167949684[5] = 0;
   out_6390642774167949684[6] = 0;
   out_6390642774167949684[7] = 1;
   out_6390642774167949684[8] = 0;
}
void h_27(double *state, double *unused, double *out_3416968408420378521) {
   out_3416968408420378521[0] = state[3];
}
void H_27(double *state, double *unused, double *out_9095144976487625047) {
   out_9095144976487625047[0] = 0;
   out_9095144976487625047[1] = 0;
   out_9095144976487625047[2] = 0;
   out_9095144976487625047[3] = 1;
   out_9095144976487625047[4] = 0;
   out_9095144976487625047[5] = 0;
   out_9095144976487625047[6] = 0;
   out_9095144976487625047[7] = 0;
   out_9095144976487625047[8] = 0;
}
void h_29(double *state, double *unused, double *out_5968445969121610433) {
   out_5968445969121610433[0] = state[1];
}
void H_29(double *state, double *unused, double *out_6666604441107109474) {
   out_6666604441107109474[0] = 0;
   out_6666604441107109474[1] = 1;
   out_6666604441107109474[2] = 0;
   out_6666604441107109474[3] = 0;
   out_6666604441107109474[4] = 0;
   out_6666604441107109474[5] = 0;
   out_6666604441107109474[6] = 0;
   out_6666604441107109474[7] = 0;
   out_6666604441107109474[8] = 0;
}
void h_28(double *state, double *unused, double *out_6453754459864711206) {
   out_6453754459864711206[0] = state[0];
}
void H_28(double *state, double *unused, double *out_6697740615532911568) {
   out_6697740615532911568[0] = 1;
   out_6697740615532911568[1] = 0;
   out_6697740615532911568[2] = 0;
   out_6697740615532911568[3] = 0;
   out_6697740615532911568[4] = 0;
   out_6697740615532911568[5] = 0;
   out_6697740615532911568[6] = 0;
   out_6697740615532911568[7] = 0;
   out_6697740615532911568[8] = 0;
}
void h_31(double *state, double *unused, double *out_2748652617803221975) {
   out_2748652617803221975[0] = state[8];
}
void H_31(double *state, double *unused, double *out_7016850876401301160) {
   out_7016850876401301160[0] = 0;
   out_7016850876401301160[1] = 0;
   out_7016850876401301160[2] = 0;
   out_7016850876401301160[3] = 0;
   out_7016850876401301160[4] = 0;
   out_7016850876401301160[5] = 0;
   out_7016850876401301160[6] = 0;
   out_7016850876401301160[7] = 0;
   out_7016850876401301160[8] = 1;
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

void car_update_25(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea) {
  update<1, 3, 0>(in_x, in_P, h_25, H_25, NULL, in_z, in_R, in_ea, MAHA_THRESH_25);
}
void car_update_24(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea) {
  update<2, 3, 0>(in_x, in_P, h_24, H_24, NULL, in_z, in_R, in_ea, MAHA_THRESH_24);
}
void car_update_30(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea) {
  update<1, 3, 0>(in_x, in_P, h_30, H_30, NULL, in_z, in_R, in_ea, MAHA_THRESH_30);
}
void car_update_26(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea) {
  update<1, 3, 0>(in_x, in_P, h_26, H_26, NULL, in_z, in_R, in_ea, MAHA_THRESH_26);
}
void car_update_27(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea) {
  update<1, 3, 0>(in_x, in_P, h_27, H_27, NULL, in_z, in_R, in_ea, MAHA_THRESH_27);
}
void car_update_29(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea) {
  update<1, 3, 0>(in_x, in_P, h_29, H_29, NULL, in_z, in_R, in_ea, MAHA_THRESH_29);
}
void car_update_28(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea) {
  update<1, 3, 0>(in_x, in_P, h_28, H_28, NULL, in_z, in_R, in_ea, MAHA_THRESH_28);
}
void car_update_31(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea) {
  update<1, 3, 0>(in_x, in_P, h_31, H_31, NULL, in_z, in_R, in_ea, MAHA_THRESH_31);
}
void car_err_fun(double *nom_x, double *delta_x, double *out_1594150801698997641) {
  err_fun(nom_x, delta_x, out_1594150801698997641);
}
void car_inv_err_fun(double *nom_x, double *true_x, double *out_3157223694652086945) {
  inv_err_fun(nom_x, true_x, out_3157223694652086945);
}
void car_H_mod_fun(double *state, double *out_501980518016513048) {
  H_mod_fun(state, out_501980518016513048);
}
void car_f_fun(double *state, double dt, double *out_3562028931429149250) {
  f_fun(state,  dt, out_3562028931429149250);
}
void car_F_fun(double *state, double dt, double *out_4547236169721199402) {
  F_fun(state,  dt, out_4547236169721199402);
}
void car_h_25(double *state, double *unused, double *out_2473458555518716086) {
  h_25(state, unused, out_2473458555518716086);
}
void car_H_25(double *state, double *unused, double *out_2649139455293893460) {
  H_25(state, unused, out_2649139455293893460);
}
void car_h_24(double *state, double *unused, double *out_5544228173403561954) {
  h_24(state, unused, out_5544228173403561954);
}
void car_H_24(double *state, double *unused, double *out_4005066002814292297) {
  H_24(state, unused, out_4005066002814292297);
}
void car_h_30(double *state, double *unused, double *out_8080346023306312171) {
  h_30(state, unused, out_8080346023306312171);
}
void car_H_30(double *state, double *unused, double *out_7176835785421501658) {
  H_30(state, unused, out_7176835785421501658);
}
void car_h_26(double *state, double *unused, double *out_7329611998958906760) {
  h_26(state, unused, out_7329611998958906760);
}
void car_H_26(double *state, double *unused, double *out_6390642774167949684) {
  H_26(state, unused, out_6390642774167949684);
}
void car_h_27(double *state, double *unused, double *out_3416968408420378521) {
  h_27(state, unused, out_3416968408420378521);
}
void car_H_27(double *state, double *unused, double *out_9095144976487625047) {
  H_27(state, unused, out_9095144976487625047);
}
void car_h_29(double *state, double *unused, double *out_5968445969121610433) {
  h_29(state, unused, out_5968445969121610433);
}
void car_H_29(double *state, double *unused, double *out_6666604441107109474) {
  H_29(state, unused, out_6666604441107109474);
}
void car_h_28(double *state, double *unused, double *out_6453754459864711206) {
  h_28(state, unused, out_6453754459864711206);
}
void car_H_28(double *state, double *unused, double *out_6697740615532911568) {
  H_28(state, unused, out_6697740615532911568);
}
void car_h_31(double *state, double *unused, double *out_2748652617803221975) {
  h_31(state, unused, out_2748652617803221975);
}
void car_H_31(double *state, double *unused, double *out_7016850876401301160) {
  H_31(state, unused, out_7016850876401301160);
}
void car_predict(double *in_x, double *in_P, double *in_Q, double dt) {
  predict(in_x, in_P, in_Q, dt);
}
void car_set_mass(double x) {
  set_mass(x);
}
void car_set_rotational_inertia(double x) {
  set_rotational_inertia(x);
}
void car_set_center_to_front(double x) {
  set_center_to_front(x);
}
void car_set_center_to_rear(double x) {
  set_center_to_rear(x);
}
void car_set_stiffness_front(double x) {
  set_stiffness_front(x);
}
void car_set_stiffness_rear(double x) {
  set_stiffness_rear(x);
}
}

const EKF car = {
  .name = "car",
  .kinds = { 25, 24, 30, 26, 27, 29, 28, 31 },
  .feature_kinds = {  },
  .f_fun = car_f_fun,
  .F_fun = car_F_fun,
  .err_fun = car_err_fun,
  .inv_err_fun = car_inv_err_fun,
  .H_mod_fun = car_H_mod_fun,
  .predict = car_predict,
  .hs = {
    { 25, car_h_25 },
    { 24, car_h_24 },
    { 30, car_h_30 },
    { 26, car_h_26 },
    { 27, car_h_27 },
    { 29, car_h_29 },
    { 28, car_h_28 },
    { 31, car_h_31 },
  },
  .Hs = {
    { 25, car_H_25 },
    { 24, car_H_24 },
    { 30, car_H_30 },
    { 26, car_H_26 },
    { 27, car_H_27 },
    { 29, car_H_29 },
    { 28, car_H_28 },
    { 31, car_H_31 },
  },
  .updates = {
    { 25, car_update_25 },
    { 24, car_update_24 },
    { 30, car_update_30 },
    { 26, car_update_26 },
    { 27, car_update_27 },
    { 29, car_update_29 },
    { 28, car_update_28 },
    { 31, car_update_31 },
  },
  .Hes = {
  },
  .sets = {
    { "mass", car_set_mass },
    { "rotational_inertia", car_set_rotational_inertia },
    { "center_to_front", car_set_center_to_front },
    { "center_to_rear", car_set_center_to_rear },
    { "stiffness_front", car_set_stiffness_front },
    { "stiffness_rear", car_set_stiffness_rear },
  },
  .extra_routines = {
  },
};

ekf_lib_init(car)
