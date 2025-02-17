# ma 투자 전략 최적화 시각화(히트맵)

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from ma_indicators_trade import MAStrategy
import pandas as pd
import numpy as np
import pyupbit
import matplotlib.pyplot as plt
from itertools import product
from datetime import datetime

def optimize_parameters():
    # 데이터 가져오기
    df = pyupbit.get_ohlcv("KRW-BTC", count=2880, interval="minute15")
    
    # 테스트할 파라미터 범위 설정
    take_profits = np.arange(0.01, 0.06, 0.005)  # 1%에서 5%까지 0.5% 단위
    stop_losses = np.arange(0.01, 0.06, 0.005)   # 1%에서 5%까지 0.5% 단위
    
    results = []
    
    # 모든 파라미터 조합에 대해 테스트
    total_combinations = len(take_profits) * len(stop_losses)
    current = 0
    
    for tp, sl in product(take_profits, stop_losses):
        current += 1
        print(f"진행률: {current}/{total_combinations} ({current/total_combinations*100:.1f}%)")
        
        strategy = MAStrategy(take_profit=tp, stop_loss=sl)
        df_with_signals = strategy.calculate_indicators(df.copy())
        _, trades = strategy.execute_strategy(df_with_signals)
        
        if trades:
            # 거래 성과 계산
            total_trades = len(trades)
            winning_trades = len([t for t in trades if t['profit'] > 0])
            total_profit = sum(t['profit'] for t in trades)
            total_profit_ratio = sum(t['profit_ratio'] for t in trades)
            max_drawdown = min(t['profit_ratio'] for t in trades)
            win_rate = winning_trades / total_trades if total_trades > 0 else 0
            
            results.append({
                'take_profit': tp * 100,  # 퍼센트로 변환
                'stop_loss': sl * 100,    # 퍼센트로 변환
                'total_trades': total_trades,
                'winning_trades': winning_trades,
                'win_rate': win_rate * 100,
                'total_profit': total_profit,
                'total_profit_ratio': total_profit_ratio * 100,
                'max_drawdown': max_drawdown * 100
            })
    
    # 결과를 데이터프레임으로 변환
    results_df = pd.DataFrame(results)
    
    # 수익률 기준으로 정렬
    results_df = results_df.sort_values('total_profit_ratio', ascending=False)
    
    # 결과 저장
    results_df.to_csv('ma_strategy_optimization.csv', index=False)
    
    # 상위 10개 결과 출력
    print("\n=== 상위 10개 파라미터 조합 ===")
    print(results_df.head(10).to_string(index=False))
    
    # 히트맵 생성
    plt.figure(figsize=(12, 8))
    pivot_table = results_df.pivot(index='stop_loss', columns='take_profit', values='total_profit_ratio')
    plt.imshow(pivot_table, cmap='RdYlGn', aspect='auto')
    plt.colorbar(label='Total Return (%)')
    
    # 축 레이블 설정 - 소수점 3자리까지 표시
    plt.xticks(range(len(take_profits)), [f'{tp*1:.3f}' for tp in take_profits], rotation=45)
    plt.yticks(range(len(stop_losses)), [f'{sl*1:.3f}' for sl in stop_losses])
    
    plt.xlabel('take_profit (%)')
    plt.ylabel('stop_loss (%)')
    plt.title('Heatmap of returns by parameter')
    
    # 한글 폰트 설정
    plt.rcParams['font.family'] = 'Malgun Gothic'  # Windows
    # plt.rcParams['font.family'] = 'AppleGothic'  # Mac
    plt.rcParams['axes.unicode_minus'] = False  # 마이너스 기호 깨짐 방지
    
    plt.tight_layout()
    
    # 그래프 저장
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    plt.savefig(f'ma_strategy_optimization_{timestamp}.png', dpi=300, bbox_inches='tight')
    
    return results_df

if __name__ == "__main__":
    print("MA 전략 최적화 시작...")
    results = optimize_parameters()
    print("\n최적화 완료!")
    print("결과는 'ma_strategy_optimization.csv'와 'ma_strategy_optimization.png'에 저장되었습니다.")
