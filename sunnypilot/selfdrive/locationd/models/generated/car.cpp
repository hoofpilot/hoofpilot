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
void err_fun(double *nom_x, double *delta_x, double *out_4802421531557453693) {
   out_4802421531557453693[0] = delta_x[0] + nom_x[0];
   out_4802421531557453693[1] = delta_x[1] + nom_x[1];
   out_4802421531557453693[2] = delta_x[2] + nom_x[2];
   out_4802421531557453693[3] = delta_x[3] + nom_x[3];
   out_4802421531557453693[4] = delta_x[4] + nom_x[4];
   out_4802421531557453693[5] = delta_x[5] + nom_x[5];
   out_4802421531557453693[6] = delta_x[6] + nom_x[6];
   out_4802421531557453693[7] = delta_x[7] + nom_x[7];
   out_4802421531557453693[8] = delta_x[8] + nom_x[8];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_4533876151458390791) {
   out_4533876151458390791[0] = -nom_x[0] + true_x[0];
   out_4533876151458390791[1] = -nom_x[1] + true_x[1];
   out_4533876151458390791[2] = -nom_x[2] + true_x[2];
   out_4533876151458390791[3] = -nom_x[3] + true_x[3];
   out_4533876151458390791[4] = -nom_x[4] + true_x[4];
   out_4533876151458390791[5] = -nom_x[5] + true_x[5];
   out_4533876151458390791[6] = -nom_x[6] + true_x[6];
   out_4533876151458390791[7] = -nom_x[7] + true_x[7];
   out_4533876151458390791[8] = -nom_x[8] + true_x[8];
}
void H_mod_fun(double *state, double *out_2305283590885064726) {
   out_2305283590885064726[0] = 1.0;
   out_2305283590885064726[1] = 0.0;
   out_2305283590885064726[2] = 0.0;
   out_2305283590885064726[3] = 0.0;
   out_2305283590885064726[4] = 0.0;
   out_2305283590885064726[5] = 0.0;
   out_2305283590885064726[6] = 0.0;
   out_2305283590885064726[7] = 0.0;
   out_2305283590885064726[8] = 0.0;
   out_2305283590885064726[9] = 0.0;
   out_2305283590885064726[10] = 1.0;
   out_2305283590885064726[11] = 0.0;
   out_2305283590885064726[12] = 0.0;
   out_2305283590885064726[13] = 0.0;
   out_2305283590885064726[14] = 0.0;
   out_2305283590885064726[15] = 0.0;
   out_2305283590885064726[16] = 0.0;
   out_2305283590885064726[17] = 0.0;
   out_2305283590885064726[18] = 0.0;
   out_2305283590885064726[19] = 0.0;
   out_2305283590885064726[20] = 1.0;
   out_2305283590885064726[21] = 0.0;
   out_2305283590885064726[22] = 0.0;
   out_2305283590885064726[23] = 0.0;
   out_2305283590885064726[24] = 0.0;
   out_2305283590885064726[25] = 0.0;
   out_2305283590885064726[26] = 0.0;
   out_2305283590885064726[27] = 0.0;
   out_2305283590885064726[28] = 0.0;
   out_2305283590885064726[29] = 0.0;
   out_2305283590885064726[30] = 1.0;
   out_2305283590885064726[31] = 0.0;
   out_2305283590885064726[32] = 0.0;
   out_2305283590885064726[33] = 0.0;
   out_2305283590885064726[34] = 0.0;
   out_2305283590885064726[35] = 0.0;
   out_2305283590885064726[36] = 0.0;
   out_2305283590885064726[37] = 0.0;
   out_2305283590885064726[38] = 0.0;
   out_2305283590885064726[39] = 0.0;
   out_2305283590885064726[40] = 1.0;
   out_2305283590885064726[41] = 0.0;
   out_2305283590885064726[42] = 0.0;
   out_2305283590885064726[43] = 0.0;
   out_2305283590885064726[44] = 0.0;
   out_2305283590885064726[45] = 0.0;
   out_2305283590885064726[46] = 0.0;
   out_2305283590885064726[47] = 0.0;
   out_2305283590885064726[48] = 0.0;
   out_2305283590885064726[49] = 0.0;
   out_2305283590885064726[50] = 1.0;
   out_2305283590885064726[51] = 0.0;
   out_2305283590885064726[52] = 0.0;
   out_2305283590885064726[53] = 0.0;
   out_2305283590885064726[54] = 0.0;
   out_2305283590885064726[55] = 0.0;
   out_2305283590885064726[56] = 0.0;
   out_2305283590885064726[57] = 0.0;
   out_2305283590885064726[58] = 0.0;
   out_2305283590885064726[59] = 0.0;
   out_2305283590885064726[60] = 1.0;
   out_2305283590885064726[61] = 0.0;
   out_2305283590885064726[62] = 0.0;
   out_2305283590885064726[63] = 0.0;
   out_2305283590885064726[64] = 0.0;
   out_2305283590885064726[65] = 0.0;
   out_2305283590885064726[66] = 0.0;
   out_2305283590885064726[67] = 0.0;
   out_2305283590885064726[68] = 0.0;
   out_2305283590885064726[69] = 0.0;
   out_2305283590885064726[70] = 1.0;
   out_2305283590885064726[71] = 0.0;
   out_2305283590885064726[72] = 0.0;
   out_2305283590885064726[73] = 0.0;
   out_2305283590885064726[74] = 0.0;
   out_2305283590885064726[75] = 0.0;
   out_2305283590885064726[76] = 0.0;
   out_2305283590885064726[77] = 0.0;
   out_2305283590885064726[78] = 0.0;
   out_2305283590885064726[79] = 0.0;
   out_2305283590885064726[80] = 1.0;
}
void f_fun(double *state, double dt, double *out_6813101336163725268) {
   out_6813101336163725268[0] = state[0];
   out_6813101336163725268[1] = state[1];
   out_6813101336163725268[2] = state[2];
   out_6813101336163725268[3] = state[3];
   out_6813101336163725268[4] = state[4];
   out_6813101336163725268[5] = dt*((-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]))*state[6] - 9.8100000000000005*state[8] + stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*state[1]) + (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*state[4])) + state[5];
   out_6813101336163725268[6] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*state[4])) + state[6];
   out_6813101336163725268[7] = state[7];
   out_6813101336163725268[8] = state[8];
}
void F_fun(double *state, double dt, double *out_1339072285061349588) {
   out_1339072285061349588[0] = 1;
   out_1339072285061349588[1] = 0;
   out_1339072285061349588[2] = 0;
   out_1339072285061349588[3] = 0;
   out_1339072285061349588[4] = 0;
   out_1339072285061349588[5] = 0;
   out_1339072285061349588[6] = 0;
   out_1339072285061349588[7] = 0;
   out_1339072285061349588[8] = 0;
   out_1339072285061349588[9] = 0;
   out_1339072285061349588[10] = 1;
   out_1339072285061349588[11] = 0;
   out_1339072285061349588[12] = 0;
   out_1339072285061349588[13] = 0;
   out_1339072285061349588[14] = 0;
   out_1339072285061349588[15] = 0;
   out_1339072285061349588[16] = 0;
   out_1339072285061349588[17] = 0;
   out_1339072285061349588[18] = 0;
   out_1339072285061349588[19] = 0;
   out_1339072285061349588[20] = 1;
   out_1339072285061349588[21] = 0;
   out_1339072285061349588[22] = 0;
   out_1339072285061349588[23] = 0;
   out_1339072285061349588[24] = 0;
   out_1339072285061349588[25] = 0;
   out_1339072285061349588[26] = 0;
   out_1339072285061349588[27] = 0;
   out_1339072285061349588[28] = 0;
   out_1339072285061349588[29] = 0;
   out_1339072285061349588[30] = 1;
   out_1339072285061349588[31] = 0;
   out_1339072285061349588[32] = 0;
   out_1339072285061349588[33] = 0;
   out_1339072285061349588[34] = 0;
   out_1339072285061349588[35] = 0;
   out_1339072285061349588[36] = 0;
   out_1339072285061349588[37] = 0;
   out_1339072285061349588[38] = 0;
   out_1339072285061349588[39] = 0;
   out_1339072285061349588[40] = 1;
   out_1339072285061349588[41] = 0;
   out_1339072285061349588[42] = 0;
   out_1339072285061349588[43] = 0;
   out_1339072285061349588[44] = 0;
   out_1339072285061349588[45] = dt*(stiffness_front*(-state[2] - state[3] + state[7])/(mass*state[1]) + (-stiffness_front - stiffness_rear)*state[5]/(mass*state[4]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[6]/(mass*state[4]));
   out_1339072285061349588[46] = -dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*pow(state[1], 2));
   out_1339072285061349588[47] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_1339072285061349588[48] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_1339072285061349588[49] = dt*((-1 - (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*pow(state[4], 2)))*state[6] - (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*pow(state[4], 2)));
   out_1339072285061349588[50] = dt*(-stiffness_front*state[0] - stiffness_rear*state[0])/(mass*state[4]) + 1;
   out_1339072285061349588[51] = dt*(-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]));
   out_1339072285061349588[52] = dt*stiffness_front*state[0]/(mass*state[1]);
   out_1339072285061349588[53] = -9.8100000000000005*dt;
   out_1339072285061349588[54] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front - pow(center_to_rear, 2)*stiffness_rear)*state[6]/(rotational_inertia*state[4]));
   out_1339072285061349588[55] = -center_to_front*dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*pow(state[1], 2));
   out_1339072285061349588[56] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_1339072285061349588[57] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_1339072285061349588[58] = dt*(-(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*pow(state[4], 2)) - (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*pow(state[4], 2)));
   out_1339072285061349588[59] = dt*(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(rotational_inertia*state[4]);
   out_1339072285061349588[60] = dt*(-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])/(rotational_inertia*state[4]) + 1;
   out_1339072285061349588[61] = center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_1339072285061349588[62] = 0;
   out_1339072285061349588[63] = 0;
   out_1339072285061349588[64] = 0;
   out_1339072285061349588[65] = 0;
   out_1339072285061349588[66] = 0;
   out_1339072285061349588[67] = 0;
   out_1339072285061349588[68] = 0;
   out_1339072285061349588[69] = 0;
   out_1339072285061349588[70] = 1;
   out_1339072285061349588[71] = 0;
   out_1339072285061349588[72] = 0;
   out_1339072285061349588[73] = 0;
   out_1339072285061349588[74] = 0;
   out_1339072285061349588[75] = 0;
   out_1339072285061349588[76] = 0;
   out_1339072285061349588[77] = 0;
   out_1339072285061349588[78] = 0;
   out_1339072285061349588[79] = 0;
   out_1339072285061349588[80] = 1;
}
void h_25(double *state, double *unused, double *out_9061235835578842003) {
   out_9061235835578842003[0] = state[6];
}
void H_25(double *state, double *unused, double *out_7208975416069729566) {
   out_7208975416069729566[0] = 0;
   out_7208975416069729566[1] = 0;
   out_7208975416069729566[2] = 0;
   out_7208975416069729566[3] = 0;
   out_7208975416069729566[4] = 0;
   out_7208975416069729566[5] = 0;
   out_7208975416069729566[6] = 1;
   out_7208975416069729566[7] = 0;
   out_7208975416069729566[8] = 0;
}
void h_24(double *state, double *unused, double *out_5781965406962125422) {
   out_5781965406962125422[0] = state[4];
   out_5781965406962125422[1] = state[5];
}
void H_24(double *state, double *unused, double *out_9060554234032672077) {
   out_9060554234032672077[0] = 0;
   out_9060554234032672077[1] = 0;
   out_9060554234032672077[2] = 0;
   out_9060554234032672077[3] = 0;
   out_9060554234032672077[4] = 1;
   out_9060554234032672077[5] = 0;
   out_9060554234032672077[6] = 0;
   out_9060554234032672077[7] = 0;
   out_9060554234032672077[8] = 0;
   out_9060554234032672077[9] = 0;
   out_9060554234032672077[10] = 0;
   out_9060554234032672077[11] = 0;
   out_9060554234032672077[12] = 0;
   out_9060554234032672077[13] = 0;
   out_9060554234032672077[14] = 1;
   out_9060554234032672077[15] = 0;
   out_9060554234032672077[16] = 0;
   out_9060554234032672077[17] = 0;
}
void h_30(double *state, double *unused, double *out_8904049167227712858) {
   out_8904049167227712858[0] = state[4];
}
void H_30(double *state, double *unused, double *out_8719435699132573423) {
   out_8719435699132573423[0] = 0;
   out_8719435699132573423[1] = 0;
   out_8719435699132573423[2] = 0;
   out_8719435699132573423[3] = 0;
   out_8719435699132573423[4] = 1;
   out_8719435699132573423[5] = 0;
   out_8719435699132573423[6] = 0;
   out_8719435699132573423[7] = 0;
   out_8719435699132573423[8] = 0;
}
void h_26(double *state, double *unused, double *out_6922026533145213466) {
   out_6922026533145213466[0] = state[7];
}
void H_26(double *state, double *unused, double *out_3467472097195673342) {
   out_3467472097195673342[0] = 0;
   out_3467472097195673342[1] = 0;
   out_3467472097195673342[2] = 0;
   out_3467472097195673342[3] = 0;
   out_3467472097195673342[4] = 0;
   out_3467472097195673342[5] = 0;
   out_3467472097195673342[6] = 0;
   out_3467472097195673342[7] = 1;
   out_3467472097195673342[8] = 0;
}
void h_27(double *state, double *unused, double *out_8391331842468009564) {
   out_8391331842468009564[0] = state[3];
}
void H_27(double *state, double *unused, double *out_7552545062776553282) {
   out_7552545062776553282[0] = 0;
   out_7552545062776553282[1] = 0;
   out_7552545062776553282[2] = 0;
   out_7552545062776553282[3] = 1;
   out_7552545062776553282[4] = 0;
   out_7552545062776553282[5] = 0;
   out_7552545062776553282[6] = 0;
   out_7552545062776553282[7] = 0;
   out_7552545062776553282[8] = 0;
}
void h_29(double *state, double *unused, double *out_6299643846419015207) {
   out_6299643846419015207[0] = state[1];
}
void H_29(double *state, double *unused, double *out_8209204354818181239) {
   out_8209204354818181239[0] = 0;
   out_8209204354818181239[1] = 1;
   out_8209204354818181239[2] = 0;
   out_8209204354818181239[3] = 0;
   out_8209204354818181239[4] = 0;
   out_8209204354818181239[5] = 0;
   out_8209204354818181239[6] = 0;
   out_8209204354818181239[7] = 0;
   out_8209204354818181239[8] = 0;
}
void h_28(double *state, double *unused, double *out_539365752793676863) {
   out_539365752793676863[0] = state[0];
}
void H_28(double *state, double *unused, double *out_5155140701821839803) {
   out_5155140701821839803[0] = 1;
   out_5155140701821839803[1] = 0;
   out_5155140701821839803[2] = 0;
   out_5155140701821839803[3] = 0;
   out_5155140701821839803[4] = 0;
   out_5155140701821839803[5] = 0;
   out_5155140701821839803[6] = 0;
   out_5155140701821839803[7] = 0;
   out_5155140701821839803[8] = 0;
}
void h_31(double *state, double *unused, double *out_1924949473881821288) {
   out_1924949473881821288[0] = state[8];
}
void H_31(double *state, double *unused, double *out_2841263994962321866) {
   out_2841263994962321866[0] = 0;
   out_2841263994962321866[1] = 0;
   out_2841263994962321866[2] = 0;
   out_2841263994962321866[3] = 0;
   out_2841263994962321866[4] = 0;
   out_2841263994962321866[5] = 0;
   out_2841263994962321866[6] = 0;
   out_2841263994962321866[7] = 0;
   out_2841263994962321866[8] = 1;
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
void car_err_fun(double *nom_x, double *delta_x, double *out_4802421531557453693) {
  err_fun(nom_x, delta_x, out_4802421531557453693);
}
void car_inv_err_fun(double *nom_x, double *true_x, double *out_4533876151458390791) {
  inv_err_fun(nom_x, true_x, out_4533876151458390791);
}
void car_H_mod_fun(double *state, double *out_2305283590885064726) {
  H_mod_fun(state, out_2305283590885064726);
}
void car_f_fun(double *state, double dt, double *out_6813101336163725268) {
  f_fun(state,  dt, out_6813101336163725268);
}
void car_F_fun(double *state, double dt, double *out_1339072285061349588) {
  F_fun(state,  dt, out_1339072285061349588);
}
void car_h_25(double *state, double *unused, double *out_9061235835578842003) {
  h_25(state, unused, out_9061235835578842003);
}
void car_H_25(double *state, double *unused, double *out_7208975416069729566) {
  H_25(state, unused, out_7208975416069729566);
}
void car_h_24(double *state, double *unused, double *out_5781965406962125422) {
  h_24(state, unused, out_5781965406962125422);
}
void car_H_24(double *state, double *unused, double *out_9060554234032672077) {
  H_24(state, unused, out_9060554234032672077);
}
void car_h_30(double *state, double *unused, double *out_8904049167227712858) {
  h_30(state, unused, out_8904049167227712858);
}
void car_H_30(double *state, double *unused, double *out_8719435699132573423) {
  H_30(state, unused, out_8719435699132573423);
}
void car_h_26(double *state, double *unused, double *out_6922026533145213466) {
  h_26(state, unused, out_6922026533145213466);
}
void car_H_26(double *state, double *unused, double *out_3467472097195673342) {
  H_26(state, unused, out_3467472097195673342);
}
void car_h_27(double *state, double *unused, double *out_8391331842468009564) {
  h_27(state, unused, out_8391331842468009564);
}
void car_H_27(double *state, double *unused, double *out_7552545062776553282) {
  H_27(state, unused, out_7552545062776553282);
}
void car_h_29(double *state, double *unused, double *out_6299643846419015207) {
  h_29(state, unused, out_6299643846419015207);
}
void car_H_29(double *state, double *unused, double *out_8209204354818181239) {
  H_29(state, unused, out_8209204354818181239);
}
void car_h_28(double *state, double *unused, double *out_539365752793676863) {
  h_28(state, unused, out_539365752793676863);
}
void car_H_28(double *state, double *unused, double *out_5155140701821839803) {
  H_28(state, unused, out_5155140701821839803);
}
void car_h_31(double *state, double *unused, double *out_1924949473881821288) {
  h_31(state, unused, out_1924949473881821288);
}
void car_H_31(double *state, double *unused, double *out_2841263994962321866) {
  H_31(state, unused, out_2841263994962321866);
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
