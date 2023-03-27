% This is a cut down version of the problem ChinaTown, useful for code examples and unit tests
% The train set is reduced from 65 cases to 20 cases and the test set is reduced from 28 to 20
% To make the series unequal length, values have arbitratily been removed from the beginning and end of series
%
@problemName UnequalMinimalGasPrices
@timestamps false
@missing false
@univariate true
@equalLength false
@targetlabel true
@data
2.39,2.36,2.45,2.45,2.54,2.69,2.63,2.73,2.7,2.73,2.68,2.76,2.76,2.68,2.39,2.4,2.36:-0.4272497972616782
3.02,3.09,3.01,3.01,2.98,3.11,3.13,3.13,3.23,3.36,3.31,3.25,3.24,3.23,3.15,3.21,3.36,3.3,3.4,3.62:-0.3330772297886702
4.07,4.35,4.25,4.33,4.45,4.65,4.77,4.71,4.66,4.97,5.13,5.21,5.39,5.66,5.52,5.32,5.25,4.96:-0.27904755897246875
2.62,2.63,2.63,2.71,2.71,2.72,2.58,2.58,2.58,2.62,2.61,2.67,2.57,2.59,2.63,2.59,2.59,2.5,2.55,2.55:-0.41383876536901176
2.44,2.43,2.47,2.48,2.5,2.57,2.65,2.62,2.63,2.75,2.76,2.72,2.77,2.79,2.73,2.91,2.98,2.91,2.86,2.96:-0.3879279331519053
3.05,3.01,3.13,3.14,3.26,3.39,3.25,3.28,3.4,3.45,3.16,3.19,3.26,3.27,3.3,3.28,3.2,3.2,3.28,3.42:-0.2238585824576708
3.11,3.11,2.93,2.85,2.95,2.88,2.75,2.75,2.56,2.52,2.63,2.63,2.44,2.54,2.54,2.59:-0.34554364217015404
1.77,1.77,2.12,2.25,2.3,2.31,2.32,2.32,2.36,2.34,2.46,2.55,2.55,2.62,2.62,2.59,2.74,2.79,2.82,2.69:-0.328501794888423
2.74,2.84,2.74,2.89,2.89,3.19,4.25,3.18,3.18,2.9,2.9,2.86,2.83,2.87,2.95,2.95,2.9:-0.3218208770339306
2.75,2.72,2.74,2.69,2.69,2.73,2.73,2.76,2.74,2.66,2.62,2.72,2.71,2.72,2.72,2.75,2.75,2.66,2.55,2.54:-0.30665818378329274
4.92,4.94,5.1,5.53,5.94,5.73,5.58,5.61,5.8,6.37,6.0,5.71,5.46,5.46,5.34,5.56,5.92,5.44,5.01,4.81:-0.32848593586912517
2.82,2.84,2.87,2.87,2.72,2.66,2.68,2.7,2.64,2.53,2.56,2.53,2.62,2.51,2.51,2.46,2.46,2.29,2.42,2.43:-0.39712400132646924
3.0,2.99,2.9,2.9,2.93,2.91,2.91,2.95,2.95,2.99,2.96,2.88,2.86,2.84,2.78,2.87,2.91,2.85,2.91,2.91:-0.3181167245484315
2.56,2.68,2.72,2.76,2.76,2.74,2.78,2.85,2.85,2.85,2.87,2.96,3.01,3.01,3.04,2.96:-0.3625439577950881
1.49,1.56,1.6,1.61,1.72,1.74,1.68,1.81,1.77,1.84,1.84,1.79,1.79,1.79,1.78,1.78,1.78,1.77,1.87,1.98:-0.19291852431801648
2.05,1.86,2.01,2.01,2.01,2.01,1.96,1.91,1.97,1.91,1.83,1.81,1.96,1.91,1.77,1.77:-0.22273496475357274
2.74,2.66,2.6,2.58,2.53,2.49,2.49,2.61,2.65,2.65,2.58,2.6,2.59,2.66,2.67,2.67,2.7,2.7,2.8,2.8:-0.5024348328319881
2.78,2.81,2.87,2.87,2.69,2.6,2.71,2.75,2.72,2.64,2.63,2.68,2.76,2.97,3.69,6.24,6.24,4.65,2.89,2.93:-0.2623629420995712
2.78,2.78,2.63,2.65,2.6,2.6,2.6,2.72,2.81,2.88,2.88,2.89,2.94,2.93,2.93,2.81,2.79,2.83,2.83,2.8:-0.3223289070794215
4.1,4.03,3.94,4.02,4.06,4.2,4.27,4.21,4.24,4.12,4.07,4.1,3.95,3.93,3.92,3.86,3.83,3.94,3.93:-0.26126071484043045