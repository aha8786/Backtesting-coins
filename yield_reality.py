
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import matplotlib.dates as mdates
import platform

# 한글 폰트 설정
platform.system() == 'Windows'
plt.rc('font', family='Malgun Gothic')
plt.rcParams['axes.unicode_minus'] = False

# 데이터 파일 읽기
df1 = pd.read_csv('trade_history_20250208_014914.csv')
df2 = pd.read_csv('trade_history_20250210_053652_cross.csv')
df3 = pd.read_csv('trade_history_20250208_031911_ma.csv')

# 각 데이터프레임의 시간 컬럼을 datetime으로 변환
def process_dataframe(df):
    if '진입일자' in df.columns:
        df['진입일자'] = pd.to_datetime(df['진입일자'])
        df = df.sort_values('진입일자')
        df['누적수익률'] = df['수익률'].cumsum()
        return df
    else:  # 다른 형식의 CSV 파일인 경우
        df.columns = df.iloc[0]  # 첫 번째 행을 컬럼명으로 설정
        df = df[1:]  # 첫 번째 행 제거
        df['진입일자'] = pd.to_datetime(df['진입일자'])
        df['수익률'] = df['수익률'].astype(float)
        df = df.sort_values('진입일자')
        df['누적수익률'] = df['수익률'].cumsum()
        return df

df1 = process_dataframe(df1)
df2 = process_dataframe(df2)
df3 = process_dataframe(df3)

# 그래프 그리기
plt.figure(figsize=(15, 8))

plt.plot(df1['진입일자'], df1['누적수익률'], label='볼린저 밴드', linewidth=2)
plt.plot(df2['진입일자'], df2['누적수익률'], label='골든/데드크로스', linewidth=2)
plt.plot(df3['진입일자'], df3['누적수익률'], label='이동평균선', linewidth=2)

# 그래프 꾸미기
plt.title('투자 전략별 누적 수익률 비교', fontsize=16, pad=20)
plt.xlabel('날짜', fontsize=12)
plt.ylabel('누적 수익률 (%)', fontsize=12)
plt.grid(True, linestyle='--', alpha=0.7)
plt.legend(fontsize=10)

# x축 날짜 포맷 설정
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=5))
plt.xticks(rotation=45)

# 여백 조정
plt.tight_layout()

# 그래프 저장
plt.savefig('strategy_comparison.png', dpi=300, bbox_inches='tight')
plt.show()
