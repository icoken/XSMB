import json

with open('historical_data.json', 'r') as f:
    data = json.load(f)

WINDOW_SIZE = 365
# 原始参数
MIN_OVERDUE = 15
MIN_GAP = 5

cost_per_bet = 10000
payout = 840000

def calculate_tail_overdue(nums):
    overdue = {t: len(nums) for t in range(10)}
    for i, item in enumerate(nums):
        tail = item['n'] % 10
        if overdue[tail] == len(nums):
            overdue[tail] = i
    return overdue

records = []
for i in range(len(data) - WINDOW_SIZE - 1, -1, -1):
    predict_date = data[i]['d']
    actual = data[i]['n']
    actual_tail = actual % 10
    
    train_data = data[i+1:i+1+WINDOW_SIZE]
    overdue = calculate_tail_overdue(train_data)
    sorted_overdue = sorted(overdue.items(), key=lambda x: -x[1])
    
    # 第1名
    tail1, days1 = sorted_overdue[0]
    gap1 = days1 - sorted_overdue[1][1]
    
    # 第2名
    tail2, days2 = sorted_overdue[1]
    gap2 = days2 - sorted_overdue[2][1] # 第2名和第3名的差距
    
    records.append({
        'date': predict_date,
        'actual_tail': actual_tail,
        'tail1': tail1,
        'days1': days1,
        'gap1': gap1,
        'tail2': tail2,
        'days2': days2,
        'gap2': gap2
    })

print("=" * 70)
print("双尾策略分析（同时投注第1名和第2名）")
print("=" * 70)
print()

# 定义策略
# 策略A: 只投第1名 (基准) - 条件: day>=15, gap>=5
# 策略B: 投第1名 + 第2名 (只要满足条件)
#       第2名的条件是否要调整？先假设和第1名一样严格，或者稍微宽松？
#       根据之前的 ranks_analysis.txt，第2名在 day>=15, gap>=5 时 ROI +4.7%
#       所以我们使用相同的条件过滤

print("参数设置:")
print(f"  遗漏天数 >= {MIN_OVERDUE}")
print(f"  Gap(与后一名差距) >= {MIN_GAP}")
print()

# 计算每天的投注和收益
daily_stats = []

for r in records:
    # 第1名是否投注
    bet1 = r['days1'] >= MIN_OVERDUE and r['gap1'] >= MIN_GAP
    # 第2名是否投注
    bet2 = r['days2'] >= MIN_OVERDUE and r['gap2'] >= MIN_GAP
    
    bets = []
    if bet1: bets.append(r['tail1'])
    if bet2: bets.append(r['tail2'])
    
    # 成本
    cost = len(bets) * 10 * cost_per_bet
    
    # 收益
    win = 0
    hit = False
    if r['actual_tail'] in bets:
        win = payout
        hit = True
        
    daily_stats.append({
        'date': r['date'],
        'bet_count': len(bets) * 10,  # 注数
        'cost': cost,
        'win': win,
        'profit': win - cost,
        'hit': hit,
        'has_bet': len(bets) > 0
    })

# 统计分析
days_with_bet = sum(1 for d in daily_stats if d['has_bet'])
total_cost = sum(d['cost'] for d in daily_stats)
total_win = sum(d['win'] for d in daily_stats)
total_profit = total_win - total_cost
total_hits = sum(1 for d in daily_stats if d['hit'])

years = len(records) / 365
annual_profit = total_profit / years

print("【双尾策略结果】")
print(f"  总天数: {len(records)}天")
print(f"  有投注天数: {days_with_bet}天")
print(f"  总投入: {total_cost:,}盾")
print(f"  总收益: {total_win:,}盾")
print(f"  总净利: {total_profit:,}盾")
print(f"  ROI: {total_profit/total_cost*100:+.1f}%")
print(f"  命中次数: {total_hits}次")
print(f"  命中频率: 平均 {days_with_bet/total_hits:.1f} 天中一次")
print(f"  年化利润: {annual_profit:,.0f}盾")
print()

# 连续不中分析
streaks = []
current = 0
for d in daily_stats:
    if d['has_bet']:
        if d['hit']:
            if current > 0:
                streaks.append(current)
            current = 0
        else:
            current += 1
if current > 0: streaks.append(current)

print("【风险分析】")
print(f"  最大连续不中: {max(streaks) if streaks else 0} 天 (原策略约36天)")
print(f"  平均连续不中: {sum(streaks)/len(streaks) if streaks else 0:.1f} 天")
print()

# 对比单尾策略 (再次计算以便同屏对比)
print("【对比: 单尾策略 (只投第1名)】")
# 快速重算
bets1 = [r for r in records if r['days1'] >= MIN_OVERDUE and r['gap1'] >= MIN_GAP]
hits1 = [r for r in bets1 if r['actual_tail'] == r['tail1']]
profit1_total = len(hits1) * payout - len(bets1) * 10 * cost_per_bet
print(f"  年化利润: {profit1_total/years:,.0f}盾")
print(f"  命中频率: 平均 {len(bets1)/len(hits1):.1f} 天中一次")
print()

print("=" * 70)
print("探索：稍微放宽第2名的条件？")
print("=" * 70)
# 之前的分析显示，第2名在 Gap>=5 时 ROI是正的。如果放宽Gap到3或0会怎样？
# 让我们测试第2名的不同Gap阈值，同时保持第1名Gap>=5不变

print(f"{'第2名Gap条件':<10} {'总ROI':<10} {'年化利润':<15} {'最大连黑':<10} {'命中频率(天)':<10}")
print("-" * 65)

for gap2_threshold in [5, 4, 3, 2, 1, 0]:
    # 模拟
    t_cost = 0
    t_win = 0
    t_hits = 0
    t_bets = 0
    
    # 连黑统计
    curr_streak = 0
    max_streak = 0
    
    for r in records:
        # 策略逻辑
        do_bet1 = r['days1'] >= 15 and r['gap1'] >= 5
        do_bet2 = r['days2'] >= 15 and r['gap2'] >= gap2_threshold
        
        bets_today = 0
        is_hit = False
        
        if do_bet1:
            bets_today += 1
            if r['actual_tail'] == r['tail1']: is_hit = True
        
        if do_bet2:
            bets_today += 1
            if r['actual_tail'] == r['tail2']: is_hit = True
            
        if bets_today > 0:
            t_bets += 1
            cost = bets_today * 10 * cost_per_bet
            win = payout if is_hit else 0
            
            t_cost += cost
            t_win += win
            if is_hit: 
                t_hits += 1
                max_streak = max(max_streak, curr_streak)
                curr_streak = 0
            else:
                curr_streak += 1
    
    max_streak = max(max_streak, curr_streak)
    roi = (t_win - t_cost) / t_cost * 100
    ann_profit = (t_win - t_cost) / years
    freq = t_bets / t_hits if t_hits > 0 else 0
    
    print(f"Gap2 >= {gap2_threshold:<7} {roi:+.1f}%    {ann_profit:,.0f}    {max_streak:<10} {freq:.1f}")
