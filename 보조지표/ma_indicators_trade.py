import pyupbit
from ta.trend import SMAIndicator, EMAIndicator
import numpy as np
import pandas as pd
from datetime import datetime
pd.set_option('display.max_rows', None)  # 모든 행 표시

class MAStrategy:
    def __init__(self, take_profit=0.03, stop_loss=0.02):
        self.position = None
        self.entry_price = None
        self.entry_date = None
        self.trade_history = []
        self.take_profit = take_profit
        self.stop_loss = stop_loss

    def calculate_indicators(self, df):
        """이동평균선 지표 계산"""
        # 데이터프레임 복사
        df = df.copy()
        
        # 이동평균선 계산
        df['sma_7'] = SMAIndicator(close=df['close'], window=7).sma_indicator()
        df['sma_15'] = SMAIndicator(close=df['close'], window=15).sma_indicator()
        df['sma_30'] = SMAIndicator(close=df['close'], window=30).sma_indicator()
        df['sma_60'] = SMAIndicator(close=df['close'], window=60).sma_indicator()
        
        # 매매 신호 생성
        df['long_signal'] = (
            (df['sma_7'] > df['sma_15']) & 
            (df['sma_15'] > df['sma_30']) & 
            (df['sma_30'] > df['sma_60'])
        )
        
        df['short_signal'] = (
            (df['sma_7'] < df['sma_15']) & 
            (df['sma_15'] < df['sma_30']) & 
            (df['sma_30'] < df['sma_60']) 
        )
        
        return df

    def execute_strategy(self, df):
        """매매 전략 실행"""
        signals = [0]  # 첫 번째 행의 신호를 0으로 초기화
        positions = [None]  # 첫 번째 행의 포지션을 None으로 초기화
        entry_prices = [None]  # 첫 번째 행의 진입가격을 None으로 초기화
        profits = [0]  # 첫 번째 행의 수익을 0으로 초기화
        
        self.position = None
        self.entry_price = None
        self.entry_date = None
        self.trade_history = []
        
        for i in range(1, len(df)):
            signal = 0
            current_price = df['close'].iloc[i]
            current_date = df.index[i]
            current_profit = 0
            
            if self.position is None:  # 포지션이 없을 때
                if df['long_signal'].iloc[i]:
                    signal = 1  # 롱 진입
                    self.position = 'long'
                    self.entry_price = current_price
                    self.entry_date = current_date
                elif df['short_signal'].iloc[i]:
                    signal = -1  # 숏 진입
                    self.position = 'short'
                    self.entry_price = current_price
                    self.entry_date = current_date
                    
            elif self.position == 'long':  # 롱 포지션 상태
                profit_ratio = (current_price - self.entry_price) / self.entry_price
                current_profit = profit_ratio
                
                # 청산 조건: sma_15 아래로 하락 또는 손익 조건 도달
                if (current_price < df['sma_15'].iloc[i] or 
                    (self.take_profit and profit_ratio >= self.take_profit) or 
                    (self.stop_loss and profit_ratio <= -self.stop_loss)):
                    
                    signal = -1  # 롱 종료
                    self.trade_history.append({
                        'entry_date': self.entry_date,
                        'exit_date': current_date,
                        'position': self.position,
                        'entry_price': self.entry_price,
                        'exit_price': current_price,
                        'profit_ratio': profit_ratio,
                        'profit': current_price - self.entry_price
                    })
                    self.position = None
                    self.entry_price = None
                    self.entry_date = None
                    
            elif self.position == 'short':  # 숏 포지션 상태
                profit_ratio = (self.entry_price - current_price) / self.entry_price
                current_profit = profit_ratio
                
                # 청산 조건: sma_15 위로 상승 또는 손익 조건 도달
                if (current_price > df['sma_15'].iloc[i] or 
                    (self.take_profit and profit_ratio >= self.take_profit) or 
                    (self.stop_loss and profit_ratio <= -self.stop_loss)):
                    
                    signal = 1  # 숏 종료
                    self.trade_history.append({
                        'entry_date': self.entry_date,
                        'exit_date': current_date,
                        'position': self.position,
                        'entry_price': self.entry_price,
                        'exit_price': current_price,
                        'profit_ratio': profit_ratio,
                        'profit': self.entry_price - current_price
                    })
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
        
        return df, self.trade_history
    
def print_trade_history(trade_history):
    """거래 내역 출력"""
    print("\n=== 거래 내역 ===")
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
    
    # CSV 파일로 저장
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_filename = f'trade_history_{timestamp}_ma.csv'
    df_trades.to_csv(csv_filename, index=False, encoding='utf-8-sig')
    print(f"\n거래 내역이 '{csv_filename}'로 저장되었습니다.")

    return total_profit

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

def main():
    # 시작 날짜 (YYYYMMDD 형식)
    start_date = "20250101"
    end_date = "20250131"
    # 시작 날짜의 다음 날짜 계산
    next_day = pd.to_datetime(end_date) + pd.Timedelta(days=1)
    next_day_str = next_day.strftime("%Y%m%d")
    # 비트코인 데이터 가져오기
    df = pyupbit.get_ohlcv("KRW-BTC", count=4500, to=next_day_str, interval="minute10")
    strategy = MAStrategy()
    df = strategy.calculate_indicators(df)
    # 시작 날짜 이후 데이터만 사용하여 매매 진행
    df = df[df.index >= start_date+'0900']

    result_df, trade_history = strategy.execute_strategy(df)

    backtest_strategy(result_df)

    # 거래 내역
    total_profit = print_trade_history(strategy.trade_history)
    # 포지션별 통계
    position_stats = get_trade_summary(strategy.trade_history)
    print("\n=== 포지션별 통계 ===")
    print(position_stats)
    # 현재 상태 출력
    print("\n현재 상태:")
    print(f"현재 가격: {result_df['close'].iloc[-1]:,} KRW")
    print(f"현재 포지션: {strategy.position}")
    print(f"진입 가격: {strategy.entry_price:,} KRW" if strategy.entry_price else "진입 가격: None")

if __name__ == "__main__":
    main()