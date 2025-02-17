import pyupbit
import pandas as pd
import numpy as np
import os
from ta.volatility import BollingerBands
from datetime import datetime

class BollingerBandStrategy:
    def __init__(self):
        self.position = None
        self.entry_price = None
        self.entry_date = None
        self.take_profit = 0.02
        self.stop_loss = 0.01
        self.trade_history = []
        
    def calculate_bollinger_bands(self, df, window=30, num_std=3):
        bb = BollingerBands(close=df['close'], window=window, window_dev=num_std)
        df['bb_upper'] = bb.bollinger_hband()
        df['bb_middle'] = bb.bollinger_mavg()
        df['bb_lower'] = bb.bollinger_lband()
        df['bb_width'] = bb.bollinger_wband()
        return df
    
    def execute_strategy(self, df):
        signals = []
        positions = []
        entry_prices = []
        profits = []
        last_position = None  # 직전 포지션 저장
        middle_touched = True  # 중간선 터치 여부 (초기값은 True로 설정)
        
        for i in range(len(df)):
            signal = 0
            current_price = df['close'].iloc[i]
            current_date = df.index[i]
            current_profit = 0
            
            # 중간선 터치 여부 확인
            if last_position is not None:
                if (last_position == 'long' and current_price <= df['bb_middle'].iloc[i]) or \
                   (last_position == 'short' and current_price >= df['bb_middle'].iloc[i]):
                    middle_touched = True
            
            if self.position is None:
                # 새로운 포지션 진입은 중간선을 터치한 후에만 가능
                if middle_touched:
                    if current_price < df['bb_lower'].iloc[i]:
                        signal = 1  # 롱 진입
                        self.position = 'long'
                        self.entry_price = current_price
                        self.entry_date = current_date
                        middle_touched = False  # 포지션 진입 후 중간선 터치 초기화
                    elif current_price > df['bb_upper'].iloc[i]:
                        signal = -1  # 숏 진입
                        self.position = 'short'
                        self.entry_price = current_price
                        self.entry_date = current_date
                        middle_touched = False  # 포지션 진입 후 중간선 터치 초기화
            
            elif self.position == 'long':
                profit_ratio = (current_price - self.entry_price) / self.entry_price
                current_profit = profit_ratio
                
                # 수익/손실 조건 또는 상단 밴드 터치로 인한 종료
                if profit_ratio >= self.take_profit or profit_ratio <= -self.stop_loss or \
                   current_price >= df['bb_upper'].iloc[i]:
                    signal = -1  # 롱 종료
                    self.trade_history.append({
                        'entry_date': self.entry_date,
                        'exit_date': current_date,
                        'position': self.position,
                        'entry_price': self.entry_price,
                        'exit_price': current_price,
                        'profit_ratio': profit_ratio,
                        'profit': current_price - self.entry_price,
                        'exit_reason': 'target_profit' if profit_ratio >= self.take_profit else 
                                     'stop_loss' if profit_ratio <= -self.stop_loss else 
                                     'bb_touch'
                    })
                    last_position = self.position  # 직전 포지션 저장
                    self.position = None
                    self.entry_price = None
                    self.entry_date = None
                    
            elif self.position == 'short':
                profit_ratio = (self.entry_price - current_price) / self.entry_price
                current_profit = profit_ratio
                
                # 수익/손실 조건 또는 하단 밴드 터치로 인한 종료
                if profit_ratio >= self.take_profit or profit_ratio <= -self.stop_loss or \
                   current_price <= df['bb_lower'].iloc[i]:
                    signal = 1  # 숏 종료
                    self.trade_history.append({
                        'entry_date': self.entry_date,
                        'exit_date': current_date,
                        'position': self.position,
                        'entry_price': self.entry_price,
                        'exit_price': current_price,
                        'profit_ratio': profit_ratio,
                        'profit': self.entry_price - current_price,
                        'exit_reason': 'target_profit' if profit_ratio >= self.take_profit else 
                                     'stop_loss' if profit_ratio <= -self.stop_loss else 
                                     'bb_touch'
                    })
                    last_position = self.position  # 직전 포지션 저장
                    self.position = None
                    self.entry_price = None
                    self.entry_date = None
            
            signals.append(signal)
            positions.append(self.position)
            entry_prices.append(self.entry_price)
            profits.append(current_profit)
            
        df['signal'] = signals
        df['position'] = positions
        df['entry_price'] = entry_prices
        df['profit'] = profits
        
        return df

def print_trade_history(trade_history, start_date):
    duration = start_date
    print("\n거래 내역:")
    print("-" * 100)
    print(f"{'포지션':<8} {'진입일자':<22} {'종료일자':<22} {'진입가격':<15} {'종료가격':<15} {'수익률':<8} {'수익금액'}")
    print("-" * 100)
    
    total_profit = 0
    for trade in trade_history:
        profit_str = f"{trade['profit_ratio']*100:+.2f}%"
        print(f"{trade['position']:<8} "
              f"{trade['entry_date'].strftime('%Y-%m-%d %H:%M:%S'):<22} "
              f"{trade['exit_date'].strftime('%Y-%m-%d %H:%M:%S'):<22} "
              f"{trade['entry_price']:,.0f} KRW"
              f"{trade['exit_price']:>15,.0f} KRW"
              f"{profit_str:>8} "
              f"{trade['profit']:>12,.0f} KRW")
        total_profit += trade['profit']
    
    print("-" * 100)
    print(f"총 수익금액: {total_profit:,.0f} KRW")
    
    # 데이터프레임 생성 및 출력
    df_trades = pd.DataFrame(trade_history)
    
    # 컬럼명 한글로 변경
    df_trades = df_trades.rename(columns={
        'position': '포지션',
        'entry_date': '진입일자',
        'exit_date': '종료일자',
        'entry_price': '진입가격',
        'exit_price': '종료가격',
        'profit_ratio': '수익률',
        'profit': '수익금액',
        'exit_reason': '종료이유'
    })
    
    # 수익률을 퍼센트로 변환
    df_trades['수익률'] = df_trades['수익률'] * 100
    
    # 데이터프레임 형식 지정
    pd.set_option('display.float_format', lambda x: f'{x:,.2f}' if isinstance(x, (float, int)) else str(x))
    
    # 거래 통계 계산
    total_trades = len(df_trades)
    winning_trades = len(df_trades[df_trades['수익률'] > 0])
    losing_trades = len(df_trades[df_trades['수익률'] <= 0])
    win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
    
    avg_profit = df_trades[df_trades['수익률'] > 0]['수익률'].mean() if winning_trades > 0 else 0
    avg_loss = df_trades[df_trades['수익률'] <= 0]['수익률'].mean() if losing_trades > 0 else 0
    
    # 거래 통계 출력
    print("\n=== 거래 통계 ===")
    print(f"총 거래 횟수: {total_trades}")
    print(f"승률: {win_rate:.2f}%")
    print(f"평균 수익: {avg_profit:.2f}%")
    print(f"평균 손실: {avg_loss:.2f}%")
    
    #CSV 파일로 저장
    # timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    # #csv_filename = f'{duration}_trade_history_{timestamp}_bb.csv'
    # csv_filename = f'{duration}_trade_history_bb.csv'
    # df_trades.to_csv(csv_filename, index=False, encoding='utf-8-sig')
    # print(f"\n거래 내역이 '{csv_filename}'로 저장되었습니다.")
    
    return df_trades, total_profit

def get_trade_summary(trade_history):
    """거래 내역 요약 통계를 반환하는 함수"""
    if not trade_history:
        return pd.DataFrame()
        
    df_trades = pd.DataFrame(trade_history)
    
    # 포지션별 통계
    position_stats = df_trades.groupby('position').agg({
        'profit_ratio': ['count', 'mean', 'std', 'min', 'max'],
        'profit': 'sum'
    }).round(4)
    
    # 컬럼명 변경
    position_stats.columns = ['거래횟수', '평균수익률', '표준편차', '최소수익률', '최대수익률', '총수익금']
    position_stats.index.name = '포지션'
    
    # 수익률 계산을 퍼센트로 변환
    for col in ['평균수익률', '최소수익률', '최대수익률']:
        position_stats[col] = position_stats[col] * 100
    
    return position_stats

def backtest_strategy(df):
    total_trades = len(df[df['signal'] != 0])
    profitable_trades = len(df[df['profit'] >= 0.02])
    loss_trades = len(df[df['profit'] <= -0.01])
    
    print("\n백테스트 결과:")
    print(f"총 거래 횟수: {total_trades}")
    print(f"이익 실현 거래: {profitable_trades}")
    print(f"손실 거래: {loss_trades}")
    
    if total_trades > 0:
        win_rate = (profitable_trades / total_trades) * 100
        print(f"승률: {win_rate:.2f}%")
# csv파일로 저장 
# def to_csv(df, filename, sum_columns=None, sum_column_name='합계'): 
#     if sum_columns is not None:
#         df.loc['합계'] = df[sum_columns].sum(axis=0)

#     if not os.path.exists(filename+'.csv'):
#         df.to_csv(filename + '.csv', index=False, mode='w', encoding='utf-8-sig')
#     else:
#         df.to_csv(filename + '.csv', index=False, mode='a', header=False, encoding='utf-8-sig')

def main():

    # 시작 날짜 (YYYYMMDD 형식)
    start_date = "20250101"
    end_date = "20250131"
    # 시작 날짜의 다음 날짜 계산
    next_day = pd.to_datetime(end_date) + pd.Timedelta(days=1)
    next_day_str = next_day.strftime("%Y%m%d")
    # 비트코인 데이터 가져오기
    df = pyupbit.get_ohlcv("KRW-BTC", count=9000, to=next_day_str, interval="minute5")
    #df = pyupbit.get_ohlcv("KRW-BTC", count=8640, interval="minute5")       # 5분봉 데이터 한달치
    
    # 전략 실행
    strategy = BollingerBandStrategy()
    df = strategy.calculate_bollinger_bands(df)
    # 시작 날짜 이후 데이터만 사용하여 매매 진행
    df = df[df.index >= start_date+'0900']

    result_df = strategy.execute_strategy(df)
    
    # 백테스트 결과 출력
    backtest_strategy(result_df)
    
    # 거래 내역 출력
    df_trades, total_profit = print_trade_history(strategy.trade_history, start_date)
    # 포지션별 통계 확인
    position_stats = get_trade_summary(strategy.trade_history)
    print("\n=== 포지션별 통계 ===")
    print(position_stats)
    #to_csv(strategy.trade_history, start_date + end_date + "bb_indicators")
    
    # 현재 상태 출력
    print("\n현재 상태:")
    print(f"현재 가격: {result_df['close'].iloc[-1]:,} KRW")
    print(f"현재 포지션: {strategy.position}")
    print(f"진입 가격: {strategy.entry_price:,} KRW" if strategy.entry_price else "진입 가격: None")
    
    # BB 밴드 정보 출력
    print("\n볼린저 밴드 정보:")
    print(f"상단 밴드: {result_df['bb_upper'].iloc[-1]:,} KRW")
    print(f"중간 밴드: {result_df['bb_middle'].iloc[-1]:,} KRW")
    print(f"하단 밴드: {result_df['bb_lower'].iloc[-1]:,} KRW")
    print(f"밴드 폭: {result_df['bb_width'].iloc[-1]:.4f}")
    
    return result_df

if __name__ == "__main__":
    result_df = main()
