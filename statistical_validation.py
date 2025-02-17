# 통계적 검증
import pandas as pd
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
import platform

plt.rc('font', family='Malgun Gothic')
plt.rcParams['axes.unicode_minus'] = False  # 마이너스 기호 깨짐 방지

class TradingStrategyTester:
    def __init__(self, bb_data, cross_data):
        # BB 전략 데이터 전처리
        self.bb_df = bb_data.copy()
        self.bb_df['수익률'] = self.bb_df['수익률'].astype(float)
        
        # Cross 전략 데이터 전처리
        self.cross_df = cross_data.copy()
        self.cross_df['수익률'] = self.cross_df['수익률'].astype(float)

    def run_statistical_tests(self):
        """두 전략의 통계적 검정 수행"""
        # 1. 두 전략의 수익률 차이에 대한 t-검정
        t_stat, p_value = stats.ttest_ind(
            self.bb_df['수익률'],
            self.cross_df['수익률']
        )
        
        # 2. 각 전략 수익률의 정규성 검정 (Shapiro-Wilk test)
        _, bb_normality_p = stats.shapiro(self.bb_df['수익률'])
        _, cross_normality_p = stats.shapiro(self.cross_df['수익률'])
        
        # 결과 저장
        test_results = {
            'T-검정 통계량': t_stat,
            'T-검정 p-value': p_value,
            'BB전략 정규성 p-value': bb_normality_p,
            'Cross전략 정규성 p-value': cross_normality_p
        }
        
        return test_results

    def plot_distribution_comparison(self):
        """두 전략의 수익률 분포 시각화"""
        plt.figure(figsize=(12, 6))
        
        # 수익률 분포 비교
        plt.subplot(1, 2, 1)
        plt.hist(self.bb_df['수익률'], bins=30, alpha=0.5, label='볼린저밴드 전략')
        plt.hist(self.cross_df['수익률'], bins=30, alpha=0.5, label='골든/데드크로스 전략')
        plt.title('수익률 분포 비교')
        plt.xlabel('수익률')
        plt.ylabel('빈도')
        plt.legend()
        
        # Q-Q plot
        plt.subplot(1, 2, 2)
        stats.probplot(self.bb_df['수익률'], dist="norm", plot=plt)
        plt.title('볼린저밴드 전략 Q-Q Plot')
        
        plt.tight_layout()
        plt.show()

        # Cross 전략의 Q-Q plot도 별도로 표시
        plt.figure(figsize=(6, 6))
        stats.probplot(self.cross_df['수익률'], dist="norm", plot=plt)
        plt.title('크로스 전략 Q-Q Plot')
        plt.tight_layout()
        plt.show()

def main():
    # 데이터 로드
    bb_df = pd.read_csv('trade_history_20250208_014914.csv')
    cross_df = pd.read_csv('trade_history_20250210_053652_cross.csv')
    
    # 분석 실행
    tester = TradingStrategyTester(bb_df, cross_df)
    results = tester.run_statistical_tests()
    
    # 결과 출력
    print("\n통계적 검정 결과:")
    print("=" * 50)
    print(f"1. 두 전략 간 수익률 차이 검정 (T-test)")
    print(f"   - 통계량: {results['T-검정 통계량']:.4f}")
    print(f"   - p-value: {results['T-검정 p-value']:.4f}")
    print(f"   - 해석: {'통계적으로 유의미한 차이 있음' if results['T-검정 p-value'] < 0.05 else '통계적으로 유의미한 차이 없음'}")
    print("\n2. 수익률 정규성 검정 (Shapiro-Wilk test)")
    print(f"   - BB 전략: p-value = {results['BB전략 정규성 p-value']:.4f}")
    print(f"   - Cross 전략: p-value = {results['Cross전략 정규성 p-value']:.4f}")
    print(f"   - 해석: p-value < 0.05 인 경우 정규분포가 아님")
    print("=" * 50)
    
    # 분포 시각화
    tester.plot_distribution_comparison()

if __name__ == "__main__":
    main()
