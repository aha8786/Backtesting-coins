# bb, cross, ma 투자 전략별 누적 수익률 비교
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import matplotlib.dates as mdates
import platform

# 한글 폰트 설정
if platform.system() == 'Windows':
    plt.rc('font', family='Malgun Gothic')
elif platform.system() == 'Darwin':  # Mac
    plt.rc('font', family='AppleGothic')
else:  # Linux
    plt.rc('font', family='NanumGothic')
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
        df['날짜'] = df['진입일자'].dt.date
        df['누적수익률'] = df['수익률'].cumsum()
        return df
    else:
        df.columns = df.iloc[0]
        df = df[1:]
        df['진입일자'] = pd.to_datetime(df['진입일자'])
        df['수익률'] = df['수익률'].astype(float)
        df = df.sort_values('진입일자')
        df['날짜'] = df['진입일자'].dt.date
        df['누적수익률'] = df['수익률'].cumsum()
        return df

df1 = process_dataframe(df1)
df2 = process_dataframe(df2)
df3 = process_dataframe(df3)

# 5일 단위로 데이터 추출
def get_5day_yields(df):
    df_daily = df.groupby('날짜')['누적수익률'].last().reset_index()
    dates = pd.date_range(start=df_daily['날짜'].min(), end=df_daily['날짜'].max(), freq='5D')
    result = []
    
    for date in dates:
        date_str = date.strftime('%Y-%m-%d')
        closest_date = df_daily[df_daily['날짜'] <= date.date()].iloc[-1]
        result.append({
            '날짜': date_str,
            '누적수익률': closest_date['누적수익률']
        })
    
    return pd.DataFrame(result)

# 각 전략별 5일 단위 수익률 계산
df1_5day = get_5day_yields(df1)
df2_5day = get_5day_yields(df2)
df3_5day = get_5day_yields(df3)

# 결과 데이터프레임 생성
result_df = pd.DataFrame({
    '날짜': df1_5day['날짜'],
    '기본 전략': df1_5day['누적수익률'].round(2),
    '크로스 전략': df2_5day['누적수익률'].round(2),
    '이동평균 전략': df3_5day['누적수익률'].round(2)
})

# 결과 출력
print("\n5일 단위 누적 수익률 (%)")
print("=" * 80)
print(result_df.to_string(index=False))
print("=" * 80)

# 그래프 그리기
plt.figure(figsize=(15, 8))

# 각 전략의 최종 수익률 계산
final_yield1 = df1_5day['누적수익률'].iloc[-1]
final_yield2 = df2_5day['누적수익률'].iloc[-1]
final_yield3 = df3_5day['누적수익률'].iloc[-1]

# 그래프 그리기
plt.plot(pd.to_datetime(df1_5day['날짜']), df1_5day['누적수익률'], 
         'o-', label=f'기본 전략 ({final_yield1:.2f}%)', linewidth=2, markersize=8)
plt.plot(pd.to_datetime(df2_5day['날짜']), df2_5day['누적수익률'], 
         's-', label=f'크로스 전략 ({final_yield2:.2f}%)', linewidth=2, markersize=8)
plt.plot(pd.to_datetime(df3_5day['날짜']), df3_5day['누적수익률'], 
         '^-', label=f'이동평균 전략 ({final_yield3:.2f}%)', linewidth=2, markersize=8)

# 마지막 지점에 수익률 텍스트 추가
last_date = pd.to_datetime(df1_5day['날짜'].iloc[-1])
plt.annotate(f'{final_yield1:.2f}%', 
            xy=(last_date, final_yield1),
            xytext=(10, 0), 
            textcoords='offset points',
            va='center')
plt.annotate(f'{final_yield2:.2f}%', 
            xy=(last_date, final_yield2),
            xytext=(10, 0), 
            textcoords='offset points',
            va='center')
plt.annotate(f'{final_yield3:.2f}%', 
            xy=(last_date, final_yield3),
            xytext=(10, 0), 
            textcoords='offset points',
            va='center')

# 그래프 꾸미기
plt.title('5일 단위 투자 전략별 누적 수익률 비교', fontsize=16, pad=20)
plt.xlabel('날짜', fontsize=12)
plt.ylabel('누적 수익률 (%)', fontsize=12)
plt.grid(True, linestyle='--', alpha=0.7)
plt.legend(fontsize=10, loc='upper left')

# x축 날짜 포맷 설정
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=5))
plt.xticks(rotation=45)

# 여백 조정 (오른쪽 여백 추가)
plt.tight_layout()
plt.subplots_adjust(right=0.95)

# 그래프 저장
#plt.savefig('strategy_comparison_5day.png', dpi=300, bbox_inches='tight')
plt.show()

# CSV 파일로 저장
result_df.to_csv('strategy_comparison_5day.csv', index=False, encoding='utf-8-sig')
print(f"\n5일 단위 누적 수익률 데이터가 'strategy_comparison_5day.csv'에 저장되었습니다.")