import pandas as pd
import os
from ta.momentum import RSIIndicator, StochRSIIndicator, WilliamsRIndicator, AwesomeOscillatorIndicator
from ta.volume import MFIIndicator, OnBalanceVolumeIndicator
from ta.trend import SMAIndicator, EMAIndicator, MACD, ADXIndicator, IchimokuIndicator, CCIIndicator, AroonIndicator
from ta.volatility import BollingerBands
import numpy as np

CLOSE_COLUMN = 'finalPrice'
HIGH_COLUMN = 'highestPrice'
LOW_COLUMN = 'lowestPrice'
VOLUME_COLUMN = 'tradeVol'
SHORT_TERM = 5
MID_TERM = 14
LONG_TERM = 28
NAME_COLUMN = 'Lval18AFC'

def find_SR(closePrice, period):
  try:
    sr = []
    for i in range(period, len(closePrice)-period):
      if closePrice[i] >= max(closePrice[i-period:i+period]) or closePrice[i] <= min(closePrice[i-period:i+period]):
        sr.append(closePrice[i])
    return sr
  except:
    pass

def add_sr_features(data:pd.DataFrame):
  try:
    period = MID_TERM
    sr = find_SR(data[CLOSE_COLUMN], period)
    print(len(sr))
    highMinDistanceSR = []
    lowMinDistanceSR = []
    closeMinDistanceSR = []
    for i in range(len(data)):
      highMinDistanceSR.append(min(list(map(lambda x: abs(x - data.loc[i, HIGH_COLUMN]),sr))))
      lowMinDistanceSR.append(min(list(map(lambda x: abs(x - data.loc[i, LOW_COLUMN]),sr))))
      closeMinDistanceSR.append(min(list(map(lambda x: abs(x - data.loc[i, CLOSE_COLUMN]),sr))))
    data['high_min_distance_sr'] = highMinDistanceSR 
    data['low_min_distance_sr'] = lowMinDistanceSR 
    data['close_min_distance_sr'] = closeMinDistanceSR 
  except:
    pass  
# cross value
def cross_value_from_bottom(column, value):
  crossed = [0] * len(column)
  try:
    for i in range(1, len(column)):
      if(column[i] >= value) and (column[i-1] < value):
        crossed[i] = 1
  except:
    pass
  return crossed

def cross_value_from_above(column, value):
  crossed = [0] * len(column)
  try:
    for i in range(1, len(column)):
      if (column[i] <= value) and (column[i-1] > value):
        crossed[i] = 1
  except:
    pass
  return crossed
 
# sum in period
def sum_of_value_in_a_period(column, period):
  if len(column) < period:
    return [0]*len(column)
  sum_in_period = [0] * len(column)
  for i in range(period):
    sum_in_period[i] = 0
  for i in range(period, len(column)):
    sum_in_period[i] = sum(column[i-period:i])
  
  return sum_in_period   

# difference from value
def difference_from_value(column, value):
  diff_from_value = [0] * len(column)
  for i in range(len(column)):
    diff_from_value[i] = column[i] - value

  return diff_from_value

# difference from line
def difference_from_line(column, line):
  diff_from_line = [0] * len(column)
  for i in range(len(column)):
    diff_from_line[i] = column[i] - line[i]

  return diff_from_line

# cross line
def cross_line_from_bottom(column, line):
  crossed = [0] * len(column)
  for i in range(1, len(column)):
    if column[i-1] < line[i-1] and column[i] >= line[i]:
        crossed[i] = 1

  return crossed
    

# TODO - what's then meaning of cross - just "=" or the similar this shit I wrote
WATCH_BACK_COLUMNS = 5
def cross_line_bullish(column, line):
  crossed = [0] * len(column)
  for i in range(WATCH_BACK_COLUMNS, len(column)):
    if(round(column[i]) == round(line[i])):
      power_of_cross = 0
      for j in range(i-WATCH_BACK_COLUMNS, i):
        if(column[j] < column[i]):
          power_of_cross += 1
      if( power_of_cross >= ((WATCH_BACK_COLUMNS/2)+1)):
        crossed[i] = 1
  
  return crossed

def cross_line_bearish(column, line):
  crossed = [0] * len(column)
  for i in range(WATCH_BACK_COLUMNS, len(column)):
    if(round(column[i]) == round(line[i])):
      power_of_cross = 0
      for j in range(i-WATCH_BACK_COLUMNS, i):
        if(column[j] > column[i]):
          power_of_cross += 1
      if( power_of_cross >= ((WATCH_BACK_COLUMNS/2)+1)):
        crossed[i] = 1
  
  return crossed

# up/down
# if you pass (A, B), this function may calculate A>B, so pass inputs in order you want
def up_down_line(column, line):
  up_down = [0] * len(column)
  for i in range(len(column)):
    if column[i]>line[i]:
      up_down[i] = 1

  return up_down


def trend_up(column, period):
  if period >= len(column):
    return [0]*len(column)
  trend = [0]*period + [1] * (len(column)-period)
  for i in range(period, len(column)):
    if min(column[i-period:i+1]) < column[i-period]:
        trend[i] = 0
  return trend

def trend_down(column, period):
  if period >= len(column):
    return [0]*len(column)
  trend = [0]*period + [1] * (len(column)-period)
  for i in range(period, len(column)):
    if max(column[i-period:i+1]) > column[i-period]:
        trend[i] = 0
  return trend

def trend_neutral(trendUp, trendDown):
  trend = [0] * len(trendUp)
  for i in range(len(trendUp)):
    if trendUp[i] == 0 and trendDown[i] == 0:
      trend[i] = 1
  return trend

def bound_expanding(upperBound, lowerBound):
    expand = [0] * len(upperBound)
    for i in range(SHORT_TERM, len(upperBound)):
        diff = -float("Inf")
        isExpand = 1
        for j in range(i-SHORT_TERM, i+1):
            if upperBound[j] - lowerBound[j]>diff:
                diff = upperBound[j] - lowerBound[j]
            else:
                isExpand = 0
        expand[i] = isExpand
        
    return expand

def bound_tightening(upperBound, lowerBound):
    tighten = [0] * len(upperBound)
    for i in range(SHORT_TERM, len(upperBound)):
        diff = float("Inf")
        isTighten = 1
        for j in range(i-SHORT_TERM, i+1):
            if upperBound[j] - lowerBound[j]<diff:
                diff = upperBound[j] - lowerBound[j]
            else:
                isTighten = 0
        tighten[i] = isTighten
        
    return tighten

def is_on_range(line, lowerBound, upperBound):
    onRange = [0] * len(line)
    for i in range(len(line)):
        if lowerBound[i] <line[i] < upperBound[i]: 
            onRange[i] = 1
    
    return onRange

def add_rsi_features(data:pd.DataFrame):
  try:
    rsi = RSIIndicator(data[CLOSE_COLUMN], fillna=True).rsi()
    data['rsi'] = rsi
    data['rsi_cross_70_from_bottom'] = cross_value_from_bottom(data['rsi'], 70)
    data['rsi_cross_70_from_above'] = cross_value_from_above(data['rsi'], 70)
    data['rsi_cross_30_from_bottom'] = cross_value_from_bottom(data['rsi'], 30)
    data['rsi_cross_30_from_above'] = cross_value_from_above(data['rsi'], 30)
    data['rsi_cross_50_from_bottom'] = cross_value_from_bottom(data['rsi'], 50)
    data['rsi_cross_50_from_above'] = cross_value_from_above(data['rsi'], 50)
    data['rsi_trendUp'] = trend_up(data['rsi'], 14)
    data['rsi_trendDown'] = trend_down(data['rsi'], 14)
  except:
    pass

def add_mfi_features(data:pd.DataFrame):
  try:
    mfi = MFIIndicator(data[HIGH_COLUMN], data[LOW_COLUMN], data[CLOSE_COLUMN], data[VOLUME_COLUMN], fillna=True).money_flow_index()
    data['mfi'] = mfi
    data['mfi_cross_80_from_bottom'] = cross_value_from_bottom(data['mfi'], 80)
    data['mfi_cross_80_from_above'] = cross_value_from_above(data['mfi'], 80)
    data['mfi_cross_20_from_bottom'] = cross_value_from_bottom(data['mfi'], 20)
    data['mfi_cross_20_from_above'] = cross_value_from_above(data['mfi'], 20)
    data['mfi_sum'] = sum_of_value_in_a_period(data['mfi'], 14)
    data['mfi_trendUp'] = trend_up(data['mfi'], 14)
    data['mfi_trendDown'] = trend_down(data['mfi'], 14)
  except:
    pass

def add_ichi_features(data:pd.DataFrame):
  try:
    ichi = IchimokuIndicator(data[HIGH_COLUMN], data[LOW_COLUMN], fillna=True)
    data['ichi_spanA'] = ichi.ichimoku_a()
    data['ichi_spanB'] = ichi.ichimoku_b()
    data['ichi_tenkan'] = ichi.ichimoku_conversion_line()
    data['ichi_kijun'] = ichi.ichimoku_base_line()
    data['ichi_diff_tenkan_price'] = difference_from_line(data['ichi_tenkan'], data[CLOSE_COLUMN])
    data['ichi_diff_kijun_price'] = difference_from_line(data['ichi_kijun'], data[CLOSE_COLUMN])
    data['ichi_diff_tenkan_kijun'] = difference_from_line(data['ichi_tenkan'], data['ichi_kijun'])
    data['ichi_diff_spanA_spanB'] = difference_from_line(data['ichi_spanA'], data['ichi_spanB'])
    data['ichi_spanA_cross_spanB_from_bottom'] = cross_line_from_bottom(data['ichi_spanA'], data['ichi_spanB'])
    data['ichi_spanA_cross_spanB_from_above'] = cross_line_from_bottom(data['ichi_spanB'], data['ichi_spanA'])

    data['ichi_price_on_greenCloud'] = is_on_range(data[CLOSE_COLUMN], data['ichi_spanB'], data['ichi_spanA'])
    data['ichi_price_on_redCloud'] = is_on_range(data[CLOSE_COLUMN], data['ichi_spanA'], data['ichi_spanB'])
  except:
    pass

def add_bb_features(data:pd.DataFrame):
  try:
    bb = BollingerBands(data[CLOSE_COLUMN], fillna=True)
    data['bb_lowerBound'] = bb.bollinger_lband()
    data['bb_upperBound'] = bb.bollinger_hband()
    data['bb_diff_upperBound_price'] = difference_from_line(data['bb_upperBound'], data[CLOSE_COLUMN])
    data['bb_diff_lowerBound_price'] = difference_from_line(data['bb_lowerBound'], data[CLOSE_COLUMN])
    data['bb_price_cross_upperBound'] = cross_line_from_bottom(data[CLOSE_COLUMN], data['bb_upperBound'])
    data['bb_price_cross_lowerBound'] = cross_line_from_bottom(data['bb_lowerBound'], data[CLOSE_COLUMN])
    
    data['bb_price_cross_upperBound_bullish'] = cross_line_bullish(data[CLOSE_COLUMN], data['bb_upperBound'])
    data['bb_price_cross_lowerBound_bearish'] = cross_line_bearish(data[CLOSE_COLUMN], data['bb_lowerBound'])
    
    data['bb_bound_expanding'] = bound_expanding(data['bb_upperBound'], data['bb_lowerBound'])
    data['bb_bound_tightening'] = bound_tightening(data['bb_upperBound'], data['bb_lowerBound'])
  except:
    pass



def add_ema_features(data:pd.DataFrame):
  try:
    ema5 = EMAIndicator(data[CLOSE_COLUMN], 5, True).ema_indicator()
    ema10 = EMAIndicator(data[CLOSE_COLUMN], 10, True).ema_indicator()
    ema20 = EMAIndicator(data[CLOSE_COLUMN], 20, True).ema_indicator()
    ema30 = EMAIndicator(data[CLOSE_COLUMN], 30, True).ema_indicator()
    ema50 = EMAIndicator(data[CLOSE_COLUMN], 50, True).ema_indicator()
    ema100 = EMAIndicator(data[CLOSE_COLUMN], 100, True).ema_indicator()
    data['ema5'] = ema5
    data['ema10'] = ema10
    data['ema20'] = ema20
    data['ema30'] = ema30
    data['ema50'] = ema50
    data['ema100'] = ema100
    #ema5
    data['ema5_cross_ema10_from_bottom'] = cross_line_from_bottom(data['ema5'], data['ema10'])
    data['ema5_cross_ema10_from_above'] = cross_line_from_bottom(data['ema10'], data['ema5'])
    data['ema5_cross_ema20_from_bottom'] = cross_line_from_bottom(data['ema5'], data['ema20'])
    data['ema5_cross_ema20_from_above'] = cross_line_from_bottom(data['ema20'], data['ema5'])
    data['ema5_cross_ema30_from_bottom'] = cross_line_from_bottom(data['ema5'], data['ema30'])
    data['ema5_cross_ema30_from_above'] = cross_line_from_bottom(data['ema30'], data['ema5'])
    data['ema5_cross_ema50_from_bottom'] = cross_line_from_bottom(data['ema5'], data['ema50'])
    data['ema5_cross_ema50_from_above'] = cross_line_from_bottom(data['ema50'], data['ema5'])
    data['ema5_cross_ema100_from_bottom'] = cross_line_from_bottom(data['ema5'], data['ema100'])
    data['ema5_cross_ema100_from_above'] = cross_line_from_bottom(data['ema100'], data['ema5'])
    
    #ema20
    data['ema20_cross_ema10_from_bottom'] = cross_line_from_bottom(data['ema20'], data['ema10'])
    data['ema20_cross_ema10_from_above'] = cross_line_from_bottom(data['ema10'], data['ema20'])
    data['ema20_cross_ema30_from_bottom'] = cross_line_from_bottom(data['ema20'], data['ema30'])
    data['ema20_cross_ema30_from_above'] = cross_line_from_bottom(data['ema30'], data['ema20'])
    data['ema20_cross_ema50_from_bottom'] = cross_line_from_bottom(data['ema20'], data['ema50'])
    data['ema20_cross_ema50_from_above'] = cross_line_from_bottom(data['ema50'], data['ema20'])
    data['ema20_cross_ema100_from_bottom'] = cross_line_from_bottom(data['ema20'], data['ema100'])
    data['ema20_cross_ema100_from_above'] = cross_line_from_bottom(data['ema100'], data['ema20'])
  except:
    pass

def add_sma_features(data:pd.DataFrame):
  try:
    sma5 = SMAIndicator(data[CLOSE_COLUMN], 5, True).sma_indicator()
    sma10 = SMAIndicator(data[CLOSE_COLUMN], 10, True).sma_indicator()
    sma20 = SMAIndicator(data[CLOSE_COLUMN], 20, True).sma_indicator()
    sma30 = SMAIndicator(data[CLOSE_COLUMN], 30, True).sma_indicator()
    sma50 = SMAIndicator(data[CLOSE_COLUMN], 50, True).sma_indicator()
    sma100 = SMAIndicator(data[CLOSE_COLUMN], 100, True).sma_indicator()
    sma200 = SMAIndicator(data[CLOSE_COLUMN], 200, True).sma_indicator()
    
    data['sma5'] = sma5
    data['sma10'] = sma10
    data['sma20'] = sma20
    data['sma30'] = sma30
    data['sma50'] = sma50
    data['sma100'] = sma100
    data['sma200'] = sma200
    
    #sma50
    data['sma50_cross_sma5_from_bottom'] = cross_line_from_bottom(data['sma50'], data['sma5'])
    data['sma50_cross_sma5_from_above'] = cross_line_from_bottom(data['sma5'], data['sma50'])
    data['sma50_cross_sma10_from_bottom'] = cross_line_from_bottom(data['sma50'], data['sma10'])
    data['sma50_cross_sma10_from_above'] = cross_line_from_bottom(data['sma10'], data['sma50'])
    data['sma50_cross_sma20_from_bottom'] = cross_line_from_bottom(data['sma50'], data['sma20'])
    data['sma50_cross_sma20_from_above'] = cross_line_from_bottom(data['sma20'], data['sma50'])
    data['sma50_cross_sma30_from_bottom'] = cross_line_from_bottom(data['sma50'], data['sma30'])
    data['sma50_cross_sma30_from_above'] = cross_line_from_bottom(data['sma30'], data['sma50'])
    data['sma50_cross_sma100_from_bottom'] = cross_line_from_bottom(data['sma50'], data['sma100'])
    data['sma50_cross_sma100_from_above'] = cross_line_from_bottom(data['sma100'], data['sma50'])
    data['sma50_cross_sma200_from_bottom'] = cross_line_from_bottom(data['sma50'], data['sma200'])
    data['sma50_cross_sma200_from_above'] = cross_line_from_bottom(data['sma200'], data['sma50'])    
    #sma200
    data['sma200_cross_sma5_from_bottom'] = cross_line_from_bottom(data['sma200'], data['sma5'])
    data['sma200_cross_sma5_from_above'] = cross_line_from_bottom(data['sma5'], data['sma200'])
    data['sma200_cross_sma10_from_bottom'] = cross_line_from_bottom(data['sma200'], data['sma10'])
    data['sma200_cross_sma10_from_above'] = cross_line_from_bottom(data['sma10'], data['sma200'])
    data['sma200_cross_sma20_from_bottom'] = cross_line_from_bottom(data['sma200'], data['sma20'])
    data['sma200_cross_sma20_from_above'] = cross_line_from_bottom(data['sma20'], data['sma200'])
    data['sma200_cross_sma30_from_bottom'] = cross_line_from_bottom(data['sma200'], data['sma30'])
    data['sma200_cross_sma30_from_above'] = cross_line_from_bottom(data['sma30'], data['sma200'])
    data['sma200_cross_sma100_from_bottom'] = cross_line_from_bottom(data['sma200'], data['sma100'])
    data['sma200_cross_sma100_from_above'] = cross_line_from_bottom(data['sma100'], data['sma200'])
  except:
    pass

def add_cci_features(data:pd.DataFrame):
  try:
    cci = CCIIndicator(data[HIGH_COLUMN], data[LOW_COLUMN], data[CLOSE_COLUMN], fillna=True).cci()
    data['cci'] = cci
    data['cci_cross_200_from_above'] = cross_value_from_above(data['cci'], 200)
    data['cci_cross_100_from_above'] = cross_value_from_above(data['cci'], 100)
    data['cci_cross_0_from_above'] = cross_value_from_above(data['cci'], 0)
    data['cci_cross_-100_from_above'] = cross_value_from_above(data['cci'], -100)
    data['cci_cross_-200_from_above'] = cross_value_from_above(data['cci'], -200)

    data['cci_cross_200_from_bottom'] = cross_value_from_bottom(data['cci'], 200)
    data['cci_cross_100_from_bottom'] = cross_value_from_bottom(data['cci'], 100)
    data['cci_cross_0_from_bottom'] = cross_value_from_bottom(data['cci'], 0)
    data['cci_cross_-100_from_bottom'] = cross_value_from_bottom(data['cci'], -100)
    data['cci_cross_-200_from_bottom'] = cross_value_from_bottom(data['cci'], -200)
    
    data['cci_sum'] = sum_of_value_in_a_period(data['cci'], 14)
  except:
    pass

def add_macd_features(data:pd.DataFrame):
  try:
    macd = MACD(data[CLOSE_COLUMN], fillna=True) 
    line = macd.macd()
    signal = macd.macd_signal()
    data['macd_macd'] = line 
    data['macd_signal'] = signal

    data['macd_macd_cross_0_from_above'] = cross_value_from_above(data['macd_macd'], 0)
    data['macd_signal_cross_0_from_above'] = cross_value_from_above(data['macd_signal'], 0)

    data['macd_macd_cross_0_from_bottom'] = cross_value_from_bottom(data['macd_macd'], 0)
    data['macd_signal_cross_0_from_bottom'] = cross_value_from_bottom(data['macd_signal'], 0)
     
    data['macd_macd_above_signal'] = up_down_line(data['macd_macd'], data['macd_signal'])
    data['macd_signal_above_macd'] = up_down_line(data['macd_signal'], data['macd_macd'])
    
    data['macd_macd_cross_signal_from_bottom'] = cross_line_from_bottom(data['macd_macd'], data['macd_signal'])
    data['macd_macd_cross_signal_from_above'] = cross_line_from_bottom(data['macd_signal'], data['macd_macd'])
    
    data['macd_macd_cross_signal_bullish'] = cross_line_bullish(data['macd_macd'], data['macd_signal'])
    data['macd_macd_cross_signal_bearish'] = cross_line_bearish(data['macd_macd'], data['macd_signal'])
  except:
    pass
    
 
def add_stochrsi_features(data:pd.DataFrame):
  try:
    stochrsi = StochRSIIndicator(data[CLOSE_COLUMN], fillna=True)
    data['stochrsi_stochrsi'] = stochrsi.stochrsi()
    data['stochrsi_d'] = stochrsi.stochrsi_d()
    data['stochrsi_k'] = stochrsi.stochrsi_k()
    
    data['stochrsi_d_cross_20_from_bottom'] = cross_value_from_bottom(data['stochrsi_d'], 20)
    data['stochrsi_d_cross_50_from_bottom'] = cross_value_from_bottom(data['stochrsi_d'], 50)
    data['stochrsi_d_cross_80_from_bottom'] = cross_value_from_bottom(data['stochrsi_d'], 80)
     
    data['stochrsi_d_cross_20_from_above'] = cross_value_from_above(data['stochrsi_d'], 20)
    data['stochrsi_d_cross_50_from_above'] = cross_value_from_above(data['stochrsi_d'], 50)
    data['stochrsi_d_cross_80_from_above'] = cross_value_from_above(data['stochrsi_d'], 80)
    
    data['stochrsi_k_cross_20_from_above'] = cross_value_from_above(data['stochrsi_k'], 20)
    data['stochrsi_k_cross_50_from_above'] = cross_value_from_above(data['stochrsi_k'], 50)
    data['stochrsi_k_cross_80_from_above'] = cross_value_from_above(data['stochrsi_k'], 80)
        
    data['stochrsi_k_cross_20_from_bottom'] = cross_value_from_bottom(data['stochrsi_k'], 20)
    data['stochrsi_k_cross_50_from_bottom'] = cross_value_from_bottom(data['stochrsi_k'], 50)
    data['stochrsi_k_cross_80_from_bottom'] = cross_value_from_bottom(data['stochrsi_k'], 80)
    
    data['stochrsi_k_cross_d_from_bottom'] = cross_line_from_bottom(data['stochrsi_k'], data['stochrsi_d'])
    data['stochrsi_k_cross_d_from_above'] = cross_line_from_bottom(data['stochrsi_d'], data['stochrsi_k'])
    
    data['stochrsi_k_cross_d_bullish'] = cross_line_bullish(data['stochrsi_k'], data['stochrsi_d'])
    data['stochrsi_k_cross_d_bearish'] = cross_line_bearish(data['stochrsi_k'], data['stochrsi_d'])
  except:
    pass

def add_trend_features(data:pd.DataFrame):
  try:
    close = data[CLOSE_COLUMN]

    data['trendUp_5'] = trend_up(close, SHORT_TERM)
    data['trendUp_14'] = trend_up(close, MID_TERM)
    data['trendUp_28'] = trend_up(close, LONG_TERM)
    data['trendUp_50'] = trend_up(close, 50)
    data['trendUp_100'] = trend_up(close, 100)
    data['trendUp_200'] = trend_up(close, 200)
    
    data['trendDown_5'] = trend_down(close, SHORT_TERM)
    data['trendDown_14'] = trend_down(close, MID_TERM)
    data['trendDown_28'] = trend_down(close, LONG_TERM)
    data['trendDown_50'] = trend_down(close, 50)
    data['trendDown_100'] = trend_down(close, 100)
    data['trendDown_200'] = trend_down(close, 200)
    
    data['trendNeutral_5'] = trend_neutral(data['trendUp_5'], data['trendDown_5'])
    data['trendNeutral_14'] = trend_neutral(data['trendUp_14'], data['trendDown_14'])
    data['trendNeutral_28'] = trend_neutral(data['trendUp_28'], data['trendDown_28'])
    data['trendNeutral_50'] = trend_neutral(data['trendUp_50'], data['trendDown_50'])
    data['trendNeutral_100'] = trend_neutral(data['trendUp_100'], data['trendDown_100'])
    data['trendNeutral_200'] = trend_neutral(data['trendUp_200'], data['trendDown_200'])
  except:
    pass

def add_wr_feature(data:pd.DataFrame):
  try:
    wr = WilliamsRIndicator(data[HIGH_COLUMN], data[LOW_COLUMN], data[CLOSE_COLUMN], fillna=True).williams_r()
    data['wr'] = wr

    data['wr_sum'] = sum_of_value_in_a_period(wr, 14)

    data['wr_cross_-20_from_above'] = cross_value_from_above(wr, -20)
    data['wr_cross_-20_from_bottom'] = cross_value_from_bottom(wr, -20)

    data['wr_cross_-50_from_above'] = cross_value_from_above(wr, -50)
    data['wr_cross_-50_from_bottom'] = cross_value_from_bottom(wr, -50)
    
    data['wr_cross_-80_from_above'] = cross_value_from_above(wr, -80)
    data['wr_cross_-80_from_bottom'] = cross_value_from_bottom(wr, -80)
  except:
    pass

def add_aroon_features(data:pd.DataFrame):
  try:
    aroon = AroonIndicator(data[CLOSE_COLUMN], fillna=True)
    data['aroon_up'] = aroon.aroon_up()
    data['aroon_down'] = aroon.aroon_down()
    data['aroon_aroon'] = aroon.aroon_indicator()

    data['aroon_up_cross_down_from_bottom'] = cross_line_from_bottom(data['aroon_up'], data['aroon_down'])        
    data['aroon_up_cross_down_from_above'] = cross_line_from_bottom(data['aroon_down'], data['aroon_up'])    
    
    data['aroon_up_above_down'] = up_down_line(data['aroon_up'], data['aroon_down'])
    data['aroon_down_above_up'] = up_down_line(data['aroon_down'], data['aroon_up'])
  except:
    pass

def add_adx_feature(data:pd.DataFrame):
  try:
    adx = ADXIndicator(data[HIGH_COLUMN], data[LOW_COLUMN], data[CLOSE_COLUMN], fillna=True) 
    data['adx_adx'] = adx.adx()
    data['adx_pos'] = adx.adx_pos()
    data['adx_neg'] = adx.adx_neg()
    
    data['adx_diff_pos_neg'] = difference_from_line(data['adx_pos'], data['adx_neg']) 
    
    data['adx_pos_cross_neg_from_bottom'] = cross_line_from_bottom(data['adx_pos'], data['adx_neg'])
    data['adx_pos_cross_neg_from_above'] = cross_line_from_bottom(data['adx_neg'], data['adx_pos'])
    
    data['adx_pos_above_neg'] = up_down_line(data['adx_pos'], data['adx_neg'])      
  except:
    pass


def add_person_company_features(data:pd.DataFrame):
  try:
    data['per_capita_person_buyer'] = data['valueOfPersonBuyer']/data['numOfPersonBuyer']
    data['per_capita_person_seller'] = data['valueOfPersonSeller']/data['numOfPersonSeller']

    data['per_capita_company_buyer'] = data['valueOfCompanyBuyer']/data['numOfCompanyBuyer']
    data['per_capita_company_seller'] = data['valueOfCompanySeller']/data['numOfCompanySeller']

    data['buy/sell_person_value'] = data['valueOfPersonBuyer'] / data['valueOfPersonSeller']
    data['buy/sell_person_volume'] = data['volOfPersonBuyer'] / data['volOfPersonSeller']
    data['buy/sell_person_num'] = data['numOfPersonBuyer'] / data['numOfPersonSeller']

    data['buy/sell_company_value'] = data['valueOfCompanyBuyer'] / data['valueOfCompanySeller']
    data['buy/sell_company_volume'] = data['volOfCompanyBuyer'] / data['volOfCompanySeller']
    data['buy/sell_company_num'] = data['numOfCompanyBuyer'] / data['numOfCompanySeller']
    
    data['buy_person/company_value'] = data['valueOfPersonBuyer'] / data['valueOfCompanyBuyer']
    data['buy_person/company_volume'] = data['volOfPersonBuyer'] / data['volOfCompanyBuyer']
    data['buy_person/company_num'] = data['numOfPersonBuyer'] / data['numOfCompanyBuyer']

    data['sell_person/company_value'] = data['valueOfPersonSeller'] / data['valueOfCompanySeller']
    data['sell_person/company_volume'] = data['volOfPersonSeller'] / data['volOfCompanySeller']
    data['sell_person/company_num'] = data['numOfPersonSeller'] / data['numOfCompanySeller']

    data['power_of_person_buyer'] = data['volOfPersonBuyer'] / data['numOfPersonBuyer']
    data['power_of_company_buyer'] = data['volOfCompanyBuyer'] / data['numOfCompanyBuyer']
    
    data['value_person_buyer_up_person_seller'] = up_down_line(data['valueOfPersonBuyer'], data['valueOfPersonSeller'])
    data['value_company_buyer_up_company_seller'] = up_down_line(data['valueOfCompanyBuyer'], data['valueOfCompanySeller'])
    data['volume_person_buyer_up_person_seller'] = up_down_line(data['volOfPersonBuyer'], data['volOfPersonSeller'])
    data['volume_company_buyer_up_company_seller'] = up_down_line(data['volOfCompanyBuyer'], data['volOfCompanySeller'])
    data['num_person_buyer_up_person_seller'] = up_down_line(data['numOfPersonBuyer'], data['numOfPersonSeller'])
    data['num_company_buyer_up_company_seller'] = up_down_line(data['numOfCompanyBuyer'], data['numOfCompanySeller'])
    
    data['value_person_seller_up_than_half_value'] = up_down_line(data['valueOfPersonSeller'], data['tradeValue']/2)
    data['volume_person_seller_up_than_half_volume'] = up_down_line(data['volOfPersonSeller'], data['tradeVol']/2)
    data['num_person_seller_up_than_half_num'] = up_down_line(data['numOfPersonSeller'], data['tradeNum']/2)
    
    data['value_person_buyer_up_than_half_value'] = up_down_line(data['valueOfPersonBuyer'], data['tradeValue']/2)
    data['volume_person_buyer_up_than_half_volume'] = up_down_line(data['volOfPersonBuyer'], data['tradeVol']/2)
    data['num_person_buyer_up_than_half_num'] = up_down_line(data['numOfPersonBuyer'], data['tradeNum']/2)

    data['value_company_seller_up_than_half_value'] = up_down_line(data['valueOfCompanySeller'], data['tradeValue']/2)
    data['volume_company_seller_up_than_half_volume'] = up_down_line(data['volOfCompanySeller'], data['tradeVol']/2)
    data['num_company_seller_up_than_half_num'] = up_down_line(data['numOfCompanySeller'], data['tradeNum']/2)


    data['value_company_buyer_up_than_half_value'] = up_down_line(data['valueOfCompanyBuyer'], data['tradeValue']/2)
    data['volume_company_buyer_up_than_half_volume'] = up_down_line(data['volOfCompanyBuyer'], data['tradeVol']/2)
    data['num_company_buyer_up_than_half_num'] = up_down_line(data['numOfCompanyBuyer'], data['tradeNum']/2)
  except:
    pass
    

def add_indicator_features(data:pd.DataFrame):
    add_rsi_features(data)
    add_mfi_features(data)
    add_ichi_features(data)
    add_bb_features(data)
    add_ema_features(data)
    add_sma_features(data)
    add_cci_features(data)
    add_macd_features(data)
    add_trend_features(data)
    add_stochrsi_features(data)
    #####################################
    add_wr_feature(data)
    add_aroon_features(data)
    add_adx_feature(data)
    

def add_features(data:pd.DataFrame):  
    data = data[data['numOfPersonBuyer'].notna()]
    names = set(data[NAME_COLUMN])
    finalData = None
    for symbol in names:
        symbolData = data[data[NAME_COLUMN] == symbol].reset_index()
        symbolData.drop(columns='index', inplace=True)
        add_indicator_features(symbolData)
        add_person_company_features(symbolData)
        add_sr_features(symbolData)
        if finalData is None:
            finalData = symbolData
        else:
            finalData = pd.concat([finalData, symbolData])
    return finalData 

