import pyupbit
from ta.momentum import RSIIndicator
from ta.trend import SMAIndicator
import pandas as pd
from datetime import datetime

class CrossStrategy:
    def __init__(self):
        self.position = None
        self.entry_price = None
        self.entry_date = None
        self.take_profit = 0.02  # 0.3% 이익/손실
        self.stop_loss = 0.01

    def calculate_indicators(self, df):
        # RSI
        df['rsi'] = RSIIndicator(close=df['close']).rsi()
        # 이동평균선
        df['sma_10'] = SMAIndicator(close=df['close'], window=10).sma_indicator()
        df['sma_34'] = SMAIndicator(close=df['close'], window=34).sma_indicator()
        
        # 골든크로스/데드크로스 조건 생성
        df['golden_cross'] = (df['sma_10'] > df['sma_34']) & (df['sma_10'].shift(1) <= df['sma_34'].shift(1))
        df['death_cross'] = (df['sma_10'] < df['sma_34']) & (df['sma_10'].shift(1) >= df['sma_34'].shift(1))
        
        return df
    
    def execute_strategy(self, df):
        trades = []
        position = None
        entry_price = None
        entry_date = None
        
        for i in range(1, len(df)):
            current_price = df['close'].iloc[i]
            current_date = df.index[i]
            
            if position is None:
                # 롱 진입 조건
                if df['golden_cross'].iloc[i] and df['rsi'].iloc[i] >= 55:
                    position = 'long'
                    entry_price = current_price
                    entry_date = current_date
                    trades.append({
                        'position': position,
                        'entry_date': entry_date,
                        'entry_price': entry_price
                    })
                
                # 숏 진입 조건
                elif df['death_cross'].iloc[i] and df['rsi'].iloc[i] <= 45:
                    position = 'short'
                    entry_price = current_price
                    entry_date = current_date
                    trades.append({
                        'position': position,
                        'entry_date': entry_date,
                        'entry_price': entry_price
                    })
            
            else:
                # 포지션별 수익률 계산
                if position == 'long':
                    profit_ratio = (current_price - entry_price) / entry_price
                    profit = current_price - entry_price
                else:  # short
                    profit_ratio = (entry_price - current_price) / entry_price
                    profit = entry_price - current_price
                
                # 청산 조건 (0.3% 이상의 이익이나 손실)
                if profit_ratio >= self.take_profit or profit_ratio <= -self.stop_loss:
                    trades[-1].update({
                        'exit_date': current_date,
                        'exit_price': current_price,
                        'profit_ratio': profit_ratio,
                        'profit': profit
                    })
                    position = None
                    entry_price = None
                    entry_date = None
        
        return trades

def print_trade_results(trades):
    # 완료된 거래만 필터링
    completed_trades = [t for t in trades if 'exit_date' in t]
    
    # 백테스트 결과 출력
    total_trades = len(completed_trades)
    profitable_trades = len([t for t in completed_trades if t['profit_ratio'] > 0])
    loss_trades = len([t for t in completed_trades if t['profit_ratio'] <= 0])
    
    print("\n백테스트 결과:")
    print(f"총 거래 횟수: {total_trades}")
    print(f"이익 실현 거래: {profitable_trades}")
    print(f"손실 거래: {loss_trades}")
    if total_trades > 0:
        print(f"승률: {(profitable_trades/total_trades*100):.2f}%")
    
    # 거래 내역 출력
    print("\n거래 내역:")
    print("-" * 100)
    print(f"{'포지션':<8} {'진입일자':<22} {'종료일자':<22} {'진입가격':<15} {'종료가격':<15} {'수익률':<8} {'수익금액'}")
    print("-" * 100)
    
    total_profit = 0
    for trade in completed_trades:
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

    df_trades = pd.DataFrame(completed_trades)
    
    # 컬럼명 한글로 변경
    df_trades = df_trades.rename(columns={
        'position': '포지션',
        'entry_date': '진입일자',
        'exit_date': '종료일자',
        'entry_price': '진입가격',
        'exit_price': '종료가격',
        'profit_ratio': '수익률',
        'profit': '수익금액'
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
    csv_filename = f'trade_history_{timestamp}_cross.csv'
    df_trades.to_csv(csv_filename, index=False, encoding='utf-8-sig')
    print(f"\n거래 내역이 '{csv_filename}'로 저장되었습니다.")
    
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
    

def main():
    start_date = "20250101"
    end_date = "20250131"
    # 시작 날짜의 다음 날짜 계산
    next_day = pd.to_datetime(end_date) + pd.Timedelta(days=1)
    next_day_str = next_day.strftime("%Y%m%d")
    # 데이터 가져오기
    df = pyupbit.get_ohlcv("KRW-BTC", count=9000, to=next_day_str, interval="minute5")
    
    # 전략 실행
    strategy = CrossStrategy()
    df = strategy.calculate_indicators(df)

    df = df[df.index >= start_date+'0900']

    trades = strategy.execute_strategy(df)
    
    # 결과 출력
    #print_trade_results(trades)
    df_trades, total_profit = print_trade_results(trades)
    # 포지션별 통계 확인
    position_stats = get_trade_summary(trades)
    print("\n=== 포지션별 통계 ===")
    print(position_stats)
    # 현재 상태 출력
    current_trade = trades[-1] if trades else None
    print("\n현재 상태:")
    print(f"현재 가격: {df['close'].iloc[-1]:,.0f} KRW")
    if current_trade and 'exit_date' not in current_trade:
        print(f"현재 포지션: {current_trade['position']}")
        print(f"진입 가격: {current_trade['entry_price']:,.0f} KRW")
    else:
        print("현재 포지션: None")
        print("진입 가격: None")

if __name__ == "__main__":
    main()