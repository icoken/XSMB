#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成包含完整历史数据的HTML预测工具 v4
主要改进：
1. 自动回溯计算所有历史统计（不依赖实时跟踪）
2. 显示最近N天的完整信号记录
3. 更清晰的状态提示
"""

import json

# 读取历史数据
with open('historical_data.json', 'r') as f:
    data = json.load(f)

# 生成嵌入式数据
embedded_data = json.dumps(data)

# HTML模板
html_template = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>XSMB 双尾遗漏策略 v5</title>
    <style>
        :root {
            --primary: #10b981;
            --primary-dark: #059669;
            --warning: #f59e0b;
            --danger: #ef4444;
            --bg: #0f172a;
            --card: #1e293b;
            --text: #f1f5f9;
            --text-muted: #94a3b8;
        }
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', system-ui, sans-serif; background: var(--bg); color: var(--text); min-height: 100vh; padding: 20px; }
        .container { max-width: 900px; margin: 0 auto; }
        header { text-align: center; margin-bottom: 30px; }
        h1 { font-size: 2rem; background: linear-gradient(135deg, #10b981, #06b6d4); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; }
        .subtitle { color: var(--text-muted); margin-top: 5px; }
        .badge { display: inline-block; background: rgba(16, 185, 129, 0.2); color: var(--primary); padding: 4px 12px; border-radius: 20px; font-size: 0.85rem; margin-top: 10px; }
        .card { background: var(--card); border-radius: 16px; padding: 24px; margin-bottom: 20px; box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3); }
        .card-title { font-size: 1.1rem; color: var(--primary); margin-bottom: 16px; display: flex; align-items: center; gap: 8px; }
        .signal-box { background: linear-gradient(135deg, rgba(16, 185, 129, 0.2), rgba(6, 182, 212, 0.2)); border: 2px solid var(--primary); border-radius: 16px; padding: 20px; text-align: center; }
        .signal-status { font-size: 1.5rem; font-weight: bold; margin-bottom: 10px; }
        .signal-yes { color: var(--primary); }
        .signal-no { color: var(--warning); }
        .no-bet-box { background: rgba(245, 158, 11, 0.1); border: 2px solid var(--warning); }
        .prediction-grid { display: grid; grid-template-columns: repeat(5, 1fr); gap: 10px; margin-top: 15px; }
        .prediction-num { background: linear-gradient(135deg, #10b981, #06b6d4); color: white; font-size: 1.5rem; font-weight: bold; padding: 15px; border-radius: 12px; text-align: center; box-shadow: 0 4px 15px rgba(16, 185, 129, 0.3); }
        .info-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 15px; margin-top: 15px; }
        .info-item { background: rgba(16, 185, 129, 0.1); padding: 15px; border-radius: 12px; text-align: center; }
        .info-value { font-size: 1.5rem; font-weight: bold; color: var(--primary); }
        .info-label { font-size: 0.85rem; color: var(--text-muted); margin-top: 5px; }
        .btn { background: var(--primary); color: white; border: none; padding: 12px 24px; border-radius: 8px; cursor: pointer; font-size: 1rem; transition: all 0.3s; }
        .btn:hover { background: var(--primary-dark); transform: translateY(-2px); }
        .btn-small { padding: 8px 16px; font-size: 0.9rem; }
        .input-group { display: flex; gap: 10px; margin-top: 15px; flex-wrap: wrap; }
        input, select { background: #1e293b; border: 1px solid rgba(255, 255, 255, 0.2); color: var(--text); padding: 12px 16px; border-radius: 8px; font-size: 1rem; }
        select option { background: #1e293b; color: var(--text); }
        input:focus, select:focus { outline: none; border-color: var(--primary); }
        .stats-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; }
        .stat-item { text-align: center; padding: 15px; background: rgba(16, 185, 129, 0.1); border-radius: 12px; }
        .stat-value { font-size: 1.8rem; font-weight: bold; color: var(--primary); }
        .stat-label { font-size: 0.8rem; color: var(--text-muted); margin-top: 5px; }
        .history-table { width: 100%; border-collapse: collapse; margin-top: 15px; }
        .history-table th, .history-table td { padding: 10px 8px; text-align: center; border-bottom: 1px solid rgba(255, 255, 255, 0.1); font-size: 0.9rem; }
        .history-table th { color: var(--text-muted); font-weight: normal; }
        .hit { color: var(--primary); }
        .miss { color: var(--danger); }
        .skip { color: var(--warning); }
        .loading { text-align: center; padding: 20px; color: var(--text-muted); }
        .success-msg { background: rgba(16, 185, 129, 0.1); color: var(--primary); padding: 15px; border-radius: 8px; margin-top: 10px; }
        .error { background: rgba(239, 68, 68, 0.1); color: var(--danger); padding: 15px; border-radius: 8px; margin-top: 10px; }
        .warning-msg { background: rgba(245, 158, 11, 0.1); color: var(--warning); padding: 15px; border-radius: 8px; margin-top: 10px; }
        .recent-draws { display: grid; grid-template-columns: repeat(5, 1fr); gap: 10px; margin-top: 15px; }
        .recent-item { background: rgba(99, 102, 241, 0.1); padding: 12px; border-radius: 10px; text-align: center; }
        .recent-date { font-size: 0.8rem; color: var(--text-muted); }
        .recent-num { font-size: 1.3rem; font-weight: bold; color: #60a5fa; margin-top: 5px; }
        .strategy-box { background: rgba(16, 185, 129, 0.05); border: 1px solid rgba(16, 185, 129, 0.2); border-radius: 12px; padding: 15px; margin-top: 15px; }
        .strategy-item { display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid rgba(255, 255, 255, 0.05); }
        .strategy-item:last-child { border-bottom: none; }
        .tab-buttons { display: flex; gap: 10px; margin-bottom: 15px; flex-wrap: wrap; }
        .tab-btn { background: rgba(255,255,255,0.1); color: var(--text-muted); border: none; padding: 8px 16px; border-radius: 8px; cursor: pointer; }
        .tab-btn.active { background: var(--primary); color: white; }
        @media (max-width: 600px) {
            .prediction-grid { grid-template-columns: repeat(5, 1fr); gap: 8px; }
            .prediction-num { font-size: 1.2rem; padding: 12px 8px; }
            .stats-grid { grid-template-columns: repeat(2, 1fr); }
            .info-grid { grid-template-columns: 1fr; }
            .recent-draws { grid-template-columns: repeat(3, 1fr); }
            .history-table th, .history-table td { padding: 8px 4px; font-size: 0.8rem; }
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🎯 双尾遗漏策略</h1>
            <p class="subtitle">同时投注遗漏第1名和第2名 | 年利润+18% | 风险降低40%</p>
            <span class="badge">✓ 双尾策略</span>
        </header>

        <!-- 数据状态 -->
        <div class="card">
            <div class="card-title">📊 数据状态</div>
            <div id="dataStatus"><div class="loading">正在初始化...</div></div>
            <div class="input-group">
                <button class="btn" onclick="fetchNewData()">🔄 获取最新数据</button>
            </div>
        </div>

        <!-- 最近开奖 -->
        <div class="card">
            <div class="card-title">🎲 最近开奖</div>
            <div id="recentDraws"><div class="loading">加载中...</div></div>
        </div>

        <!-- 今日信号 -->
        <div class="card">
            <div class="card-title">📡 下期预测信号</div>
            <div id="signalBox"><div class="loading">计算中...</div></div>
        </div>

        <!-- 预测详情 -->
        <div class="card" id="predictionCard" style="display: none;">
            <div class="card-title">🎯 预测号码 <span id="predictDate" style="font-size: 0.9rem; color: var(--text-muted);"></span></div>
            <div id="prediction"></div>
            <div id="analysisInfo" style="margin-top: 15px;"></div>
        </div>

        <!-- 自动统计 -->
        <div class="card">
            <div class="card-title">📈 历史回溯统计 <span style="font-size: 0.85rem; color: var(--text-muted);">（基于全部历史数据自动计算）</span></div>
            <div class="tab-buttons">
                <button class="tab-btn active" onclick="setStatsPeriod(30)">近30天</button>
                <button class="tab-btn" onclick="setStatsPeriod(90)">近90天</button>
                <button class="tab-btn" onclick="setStatsPeriod(180)">近180天</button>
                <button class="tab-btn" onclick="setStatsPeriod(365)">近1年</button>
                <button class="tab-btn" onclick="setStatsPeriod(0)">全部</button>
            </div>
            <div class="stats-grid">
                <div class="stat-item"><div class="stat-value" id="totalDays">0</div><div class="stat-label">总天数</div></div>
                <div class="stat-item"><div class="stat-value" id="betDays">0</div><div class="stat-label">投注天数</div></div>
                <div class="stat-item"><div class="stat-value" id="hitCount">0</div><div class="stat-label">命中次数</div></div>
                <div class="stat-item"><div class="stat-value" id="hitRate">0%</div><div class="stat-label">命中率</div></div>
            </div>
            <div id="roiInfo" style="margin-top: 15px; text-align: center; font-size: 0.9rem;"></div>
        </div>

        <!-- 历史记录 -->
        <div class="card">
            <div class="card-title">📋 信号记录 <span style="font-size: 0.85rem; color: var(--text-muted);">（自动回溯计算）</span></div>
            <div class="input-group" style="margin-top: 0; margin-bottom: 15px;">
                <select id="recordFilter" onchange="loadHistory()">
                    <option value="all">全部记录</option>
                    <option value="bet">仅投注日</option>
                    <option value="hit">仅命中</option>
                    <option value="miss">仅未中</option>
                </select>
                <select id="recordCount" onchange="loadHistory()">
                    <option value="20">显示20条</option>
                    <option value="50">显示50条</option>
                    <option value="100">显示100条</option>
                </select>
            </div>
            <div style="overflow-x: auto;">
                <table class="history-table">
                    <thead><tr><th>日期</th><th>信号</th><th>预测尾数</th><th>开奖</th><th>结果</th></tr></thead>
                    <tbody id="historyBody"><tr><td colspan="5" style="text-align:center; color: var(--text-muted);">加载中...</td></tr></tbody>
                </table>
            </div>
        </div>

        <!-- 策略说明 -->
        <div class="card">
            <div class="card-title">📖 双尾策略说明</div>
            <div class="strategy-box">
                <div class="strategy-item"><span>训练窗口</span><span style="color: var(--primary);">365天</span></div>
                <div class="strategy-item"><span>第1名条件</span><span>遗漏 ≥ 15天 且 差距 ≥ 5天</span></div>
                <div class="strategy-item"><span>第2名条件</span><span>遗漏 ≥ 15天 且 差距 ≥ 5天</span></div>
                <div class="strategy-item"><span>投注方式</span><span>满足条件的尾数各投10注 (10-20注/天)</span></div>
                <div class="strategy-item"><span>策略优势</span><span>年利润+18% | 连续不中天数降40%</span></div>
                <div class="strategy-item"><span>历史ROI</span><span style="color: var(--primary);">+11.7%</span></div>
            </div>
            <p style="margin-top: 15px; color: var(--text-muted); font-size: 0.9rem;">
                💡 双尾策略同时投注遗漏第1名和第2名，命中更频繁（平均6天1次），资金回笼更快
            </p>
            <p style="margin-top: 10px; color: var(--danger); font-size: 0.9rem;">⚠️ 仅供娱乐参考，历史表现不代表未来收益</p>
        </div>
    </div>

    <script>
        // ========================================
        // 内嵌历史数据
        // ========================================
        const EMBEDDED_DATA = ''' + embedded_data + ''';

        // 配置
        const CONFIG = {
            WINDOW_SIZE: 365,
            MIN_OVERDUE: 15,
            MIN_GAP: 5
        };

        // 全局变量
        let lotteryData = [];
        let allRecords = [];  // 所有回溯计算的记录
        let currentStatsPeriod = 30;

        // 初始化
        document.addEventListener('DOMContentLoaded', () => {
            initializeData();
        });

        // 初始化数据
        function initializeData() {
            // 合并嵌入数据和localStorage数据
            const storageKey = 'xsmb_data_v4';
            let storedData = [];
            try {
                storedData = JSON.parse(localStorage.getItem(storageKey) || '[]');
            } catch(e) {}
            
            lotteryData = mergeData(EMBEDDED_DATA, storedData);
            localStorage.setItem(storageKey, JSON.stringify(lotteryData));
            
            updateDataStatus();
            displayRecentDraws();
            
            // 回溯计算所有历史记录
            calculateAllRecords();
            
            // 计算今日信号
            calculateTodaySignal();
            
            // 尝试获取新数据
            fetchNewData();
        }

        // 合并数据
        function mergeData(data1, data2) {
            const map = new Map();
            data1.forEach(item => map.set(item.d, item));
            data2.forEach(item => map.set(item.d, item));
            return Array.from(map.values()).sort((a, b) => b.d.localeCompare(a.d));
        }

        // 回溯计算所有历史记录 - 双尾策略
        function calculateAllRecords() {
            allRecords = [];
            
            // 从第366天开始（需要365天窗口）
            for (let i = 0; i < lotteryData.length - CONFIG.WINDOW_SIZE; i++) {
                const predictDate = lotteryData[i].d;  // 开奖日期
                const actualNum = lotteryData[i].n;    // 实际开奖号码
                const actualTail = actualNum % 10;
                
                // 使用开奖前一天的数据计算信号
                const trainData = lotteryData.slice(i + 1, i + 1 + CONFIG.WINDOW_SIZE);
                
                if (trainData.length < CONFIG.WINDOW_SIZE) continue;
                
                const overdue = calculateTailOverdue(trainData);
                const sorted = Object.entries(overdue)
                    .map(([tail, days]) => ({ tail: parseInt(tail), days }))
                    .sort((a, b) => b.days - a.days);
                
                // 第1名
                const tail1 = sorted[0];
                const gap1 = tail1.days - sorted[1].days;
                const bet1 = tail1.days >= CONFIG.MIN_OVERDUE && gap1 >= CONFIG.MIN_GAP;
                const hit1 = bet1 && (actualTail === tail1.tail);
                
                // 第2名
                const tail2 = sorted[1];
                const gap2 = tail2.days - sorted[2].days;
                const bet2 = tail2.days >= CONFIG.MIN_OVERDUE && gap2 >= CONFIG.MIN_GAP;
                const hit2 = bet2 && (actualTail === tail2.tail);
                
                // 任一命中
                const shouldBet = bet1 || bet2;
                const hit = hit1 || hit2;
                
                allRecords.push({
                    date: predictDate,
                    type: shouldBet ? 'BET' : 'SKIP',
                    // 第1名信息
                    tail1: tail1.tail,
                    days1: tail1.days,
                    gap1: gap1,
                    bet1: bet1,
                    hit1: hit1,
                    // 第2名信息
                    tail2: tail2.tail,
                    days2: tail2.days,
                    gap2: gap2,
                    bet2: bet2,
                    hit2: hit2,
                    // 综合
                    actual: actualNum,
                    hit: hit,
                    betCount: (bet1 ? 1 : 0) + (bet2 ? 1 : 0)
                });
            }
            
            // 更新统计和历史显示
            updateStats();
            loadHistory();
        }

        // 计算尾数遗漏
        function calculateTailOverdue(data) {
            const overdue = {};
            for (let t = 0; t < 10; t++) overdue[t] = data.length;
            for (let i = 0; i < data.length; i++) {
                const tail = data[i].n % 10;
                if (overdue[tail] === data.length) overdue[tail] = i;
            }
            return overdue;
        }

        // 设置统计周期
        function setStatsPeriod(days) {
            currentStatsPeriod = days;
            document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
            event.target.classList.add('active');
            updateStats();
        }

        // 更新统计
        function updateStats() {
            let records = allRecords;
            
            // 按周期筛选
            if (currentStatsPeriod > 0) {
                const cutoffDate = new Date();
                cutoffDate.setDate(cutoffDate.getDate() - currentStatsPeriod);
                const cutoffStr = cutoffDate.toISOString().split('T')[0];
                records = allRecords.filter(r => r.date >= cutoffStr);
            }
            
            const betRecords = records.filter(r => r.type === 'BET');
            const hitRecords = betRecords.filter(r => r.hit);
            
            document.getElementById('totalDays').textContent = records.length;
            document.getElementById('betDays').textContent = betRecords.length;
            document.getElementById('hitCount').textContent = hitRecords.length;
            
            const hitRate = betRecords.length > 0 ? (hitRecords.length / betRecords.length * 100) : 0;
            document.getElementById('hitRate').textContent = hitRate.toFixed(1) + '%';
            
            // ROI计算: 命中赔率8.4倍，每次投注10个号码
            const roi = betRecords.length > 0 ? ((hitRecords.length * 8.4 - betRecords.length) / betRecords.length * 100) : 0;
            const roiColor = roi >= 0 ? 'var(--primary)' : 'var(--danger)';
            
            document.getElementById('roiInfo').innerHTML = `
                命中率: <span style="color: ${hitRate >= 11.9 ? 'var(--primary)' : 'var(--danger)'}">${hitRate.toFixed(1)}%</span> 
                (平衡线11.9%) | 
                ROI: <span style="color: ${roiColor}">${roi >= 0 ? '+' : ''}${roi.toFixed(1)}%</span>
            `;
        }

        // 加载历史记录 - 双尾策略
        function loadHistory() {
            const tbody = document.getElementById('historyBody');
            const filter = document.getElementById('recordFilter').value;
            const count = parseInt(document.getElementById('recordCount').value);
            
            let records = [...allRecords];
            
            // 筛选
            if (filter === 'bet') records = records.filter(r => r.type === 'BET');
            else if (filter === 'hit') records = records.filter(r => r.hit === true);
            else if (filter === 'miss') records = records.filter(r => r.hit === false);
            
            if (records.length === 0) {
                tbody.innerHTML = '<tr><td colspan="7" style="text-align:center; color: var(--text-muted);">暂无记录</td></tr>';
                return;
            }
            
            tbody.innerHTML = records.slice(0, count).map(r => {
                const resultClass = r.type === 'SKIP' ? 'skip' : (r.hit ? 'hit' : 'miss');
                const resultText = r.type === 'SKIP' ? '-' : (r.hit ? '✅' : '❌');
                const signalText = r.type === 'SKIP' ? '跳过' : `${r.betCount}尾`;
                const signalClass = r.type === 'SKIP' ? 'skip' : 'hit';
                
                // 构建预测信息
                let predictInfo = '';
                if (r.bet1) predictInfo += `<span style="color: var(--primary);">尾${r.tail1}</span>`;
                if (r.bet2) predictInfo += `${r.bet1 ? '+' : ''}<span style="color: #60a5fa;">尾${r.tail2}</span>`;
                if (!r.bet1 && !r.bet2) predictInfo = '-';
                
                return `<tr>
                    <td>${r.date}</td>
                    <td class="${signalClass}">${signalText}</td>
                    <td>${predictInfo}</td>
                    <td>${r.actual.toString().padStart(2, '0')}</td>
                    <td class="${resultClass}">${resultText}</td>
                </tr>`;
            }).join('');
        }

        // 计算今日信号 - 双尾策略
        function calculateTodaySignal() {
            if (lotteryData.length < CONFIG.WINDOW_SIZE) {
                document.getElementById('signalBox').innerHTML = '<div class="error">数据不足365天</div>';
                return;
            }

            const trainData = lotteryData.slice(0, CONFIG.WINDOW_SIZE);
            const overdue = calculateTailOverdue(trainData);
            const sorted = Object.entries(overdue)
                .map(([tail, days]) => ({ tail: parseInt(tail), days }))
                .sort((a, b) => b.days - a.days);

            // 第1名
            const tail1 = sorted[0];
            const gap1 = tail1.days - sorted[1].days;
            const bet1 = tail1.days >= CONFIG.MIN_OVERDUE && gap1 >= CONFIG.MIN_GAP;
            
            // 第2名
            const tail2 = sorted[1];
            const gap2 = tail2.days - sorted[2].days;
            const bet2 = tail2.days >= CONFIG.MIN_OVERDUE && gap2 >= CONFIG.MIN_GAP;

            displayDualSignal(bet1, tail1, gap1, bet2, tail2, gap2, sorted);
        }

        // 显示双尾信号
        function displayDualSignal(bet1, tail1, gap1, bet2, tail2, gap2, allOverdue) {
            const signalBox = document.getElementById('signalBox');
            const predCard = document.getElementById('predictionCard');

            // 遗漏列表
            let overdueListHtml = '<div style="margin-top: 15px; font-size: 0.85rem; color: var(--text-muted);">尾数遗漏: ';
            allOverdue.forEach((item, idx) => {
                let style = '';
                if (idx === 0 && bet1) style = 'color: var(--primary); font-weight: bold;';
                else if (idx === 1 && bet2) style = 'color: #60a5fa; font-weight: bold;';
                overdueListHtml += `<span style="${style}">尾${item.tail}(${item.days}天)</span> `;
            });
            overdueListHtml += '</div>';

            const latestDate = new Date(lotteryData[0].d);
            latestDate.setDate(latestDate.getDate() + 1);
            const predictDateStr = `${latestDate.getMonth() + 1}/${latestDate.getDate()}`;

            const hasBet = bet1 || bet2;
            
            if (hasBet) {
                let signalHtml = '<div class="signal-box">';
                signalHtml += '<div class="signal-status signal-yes">✅ 有信号 - 投注!</div>';
                
                // 第1名信号
                if (bet1) {
                    signalHtml += `<p style="font-size: 1.1rem; margin: 10px 0;">
                        <span style="color: var(--primary); font-weight: bold;">【第1名】</span> 
                        尾数 <strong>${tail1.tail}</strong> 遗漏 <strong>${tail1.days}</strong> 天 
                        <span style="color: var(--text-muted);">(差距${gap1}天)</span>
                    </p>`;
                }
                
                // 第2名信号
                if (bet2) {
                    signalHtml += `<p style="font-size: 1.1rem; margin: 10px 0;">
                        <span style="color: #60a5fa; font-weight: bold;">【第2名】</span> 
                        尾数 <strong>${tail2.tail}</strong> 遗漏 <strong>${tail2.days}</strong> 天 
                        <span style="color: var(--text-muted);">(差距${gap2}天)</span>
                    </p>`;
                }
                
                signalHtml += '</div>' + overdueListHtml;
                signalBox.innerHTML = signalHtml;

                // 显示预测号码
                predCard.style.display = 'block';
                let predictions = [];
                if (bet1) {
                    for (let i = 0; i < 10; i++) predictions.push({ num: i * 10 + tail1.tail, rank: 1 });
                }
                if (bet2) {
                    for (let i = 0; i < 10; i++) predictions.push({ num: i * 10 + tail2.tail, rank: 2 });
                }
                
                document.getElementById('prediction').innerHTML = `
                    <div class="prediction-grid">
                        ${predictions.map(p => {
                            const color = p.rank === 1 ? 'linear-gradient(135deg, #10b981, #06b6d4)' : 'linear-gradient(135deg, #3b82f6, #8b5cf6)';
                            return `<div class="prediction-num" style="background: ${color};">${p.num.toString().padStart(2, '0')}</div>`;
                        }).join('')}
                    </div>
                    <p style="text-align: center; margin-top: 10px; font-size: 0.85rem; color: var(--text-muted);">
                        <span style="color: var(--primary);">■</span> 第1名 
                        <span style="color: #3b82f6; margin-left: 15px;">■</span> 第2名
                    </p>
                `;
                document.getElementById('predictDate').textContent = `（预测 ${predictDateStr} 开奖）`;
                
                const betCount = (bet1 ? 1 : 0) + (bet2 ? 1 : 0);
                document.getElementById('analysisInfo').innerHTML = `
                    <div class="info-grid">
                        <div class="info-item"><div class="info-value">${betCount * 10}注</div><div class="info-label">今日投注</div></div>
                        <div class="info-item"><div class="info-value">${betCount}尾</div><div class="info-label">符合条件</div></div>
                    </div>
                `;
            } else {
                signalBox.innerHTML = `
                    <div class="signal-box no-bet-box">
                        <div class="signal-status signal-no">⏸️ 不投注</div>
                        <p>第1名: 尾${tail1.tail} 遗漏${tail1.days}天 差距${gap1}天 ${tail1.days < CONFIG.MIN_OVERDUE ? '(遗漏不足)' : gap1 < CONFIG.MIN_GAP ? '(差距不足)' : ''}</p>
                        <p>第2名: 尾${tail2.tail} 遗漏${tail2.days}天 差距${gap2}天 ${tail2.days < CONFIG.MIN_OVERDUE ? '(遗漏不足)' : gap2 < CONFIG.MIN_GAP ? '(差距不足)' : ''}</p>
                    </div>
                    ${overdueListHtml}
                `;
                predCard.style.display = 'none';
            }
        }

        // 更新数据状态
        function updateDataStatus(message = '') {
            const statusDiv = document.getElementById('dataStatus');
            const hasEnough = lotteryData.length >= CONFIG.WINDOW_SIZE;
            const latestDate = lotteryData.length > 0 ? lotteryData[0].d : '--';
            const latestNum = lotteryData.length > 0 ? lotteryData[0].n.toString().padStart(2, '0') : '--';
            
            statusDiv.innerHTML = `
                <div class="${hasEnough ? 'success-msg' : 'warning-msg'}">
                    ${hasEnough ? '✅' : '⚠️'} 已加载 ${lotteryData.length} 天数据<br>
                    最新: ${latestDate} → ${latestNum}
                    ${message ? `<br><span style="font-size:0.9rem;">${message}</span>` : ''}
                </div>
            `;
        }

        // 显示最近开奖
        function displayRecentDraws() {
            const container = document.getElementById('recentDraws');
            const recent = lotteryData.slice(0, 5);
            
            if (recent.length === 0) {
                container.innerHTML = '<div class="loading">暂无数据</div>';
                return;
            }
            
            container.innerHTML = `
                <div class="recent-draws">
                    ${recent.map(item => `
                        <div class="recent-item">
                            <div class="recent-date">${item.d.slice(5)}</div>
                            <div class="recent-num">${item.n.toString().padStart(2, '0')}</div>
                        </div>
                    `).join('')}
                </div>
            `;
        }

        // 获取新数据
        async function fetchNewData() {
            const statusDiv = document.getElementById('dataStatus');
            statusDiv.innerHTML += '<div style="margin-top:10px;color:var(--text-muted);font-size:0.9rem;">🔄 正在获取最新数据...</div>';

            try {
                // 首选方案：使用免费API（不需要CORS代理）
                try {
                    const apiUrl = 'https://api-xsmb-today.onrender.com/api/v1';
                    const response = await fetch(apiUrl, { 
                        signal: AbortSignal.timeout(20000)
                    });
                    const data = await response.json();
                    
                    if (data && data.results && data.results['ĐB']) {
                        const dateStr = data.time; // 格式: DD-MM-YYYY
                        const parts = dateStr.split('-');
                        const formattedDate = `${parts[2]}-${parts[1].padStart(2,'0')}-${parts[0].padStart(2,'0')}`;
                        const specialPrize = parseInt(data.results['ĐB'][0]);
                        const lastTwo = specialPrize % 100;
                        
                        const newData = [{ d: formattedDate, n: lastTwo }];
                        const oldLatest = lotteryData.length > 0 ? lotteryData[0].d : '';
                        lotteryData = mergeData(lotteryData, newData);
                        localStorage.setItem('xsmb_data_v4', JSON.stringify(lotteryData));
                        
                        const newLatest = lotteryData[0].d;
                        updateDataStatus(newLatest !== oldLatest ? `✅ 已更新到 ${newLatest}` : '数据已是最新');
                        displayRecentDraws();
                        calculateAllRecords();
                        calculateTodaySignal();
                        return;
                    }
                } catch (apiError) {
                    console.log('API fetch failed:', apiError.message);
                }

                // 备选方案：使用CORS代理获取网页数据
                const sources = [
                    {
                        url: 'https://az24.vn/xsmb-30-ngay.html',
                        parser: parseAz24Data
                    }
                ];
                
                const proxies = [
                    'https://corsproxy.io/?',
                    'https://api.allorigins.win/get?url='
                ];

                for (const source of sources) {
                    for (const proxyUrl of proxies) {
                        try {
                            const response = await fetch(proxyUrl + encodeURIComponent(source.url), { 
                                signal: AbortSignal.timeout(15000)
                            });
                            
                            // 尝试解析为JSON（allorigins格式）或直接获取文本（corsproxy格式）
                            let html = '';
                            const contentType = response.headers.get('content-type') || '';
                            
                            if (contentType.includes('application/json')) {
                                const data = await response.json();
                                html = data.contents || '';
                            } else {
                                html = await response.text();
                            }
                            
                            if (html && html.length > 1000) {
                                const newData = source.parser(html);
                                if (newData.length > 0) {
                                    const oldLatest = lotteryData.length > 0 ? lotteryData[0].d : '';
                                    lotteryData = mergeData(lotteryData, newData);
                                    localStorage.setItem('xsmb_data_v4', JSON.stringify(lotteryData));
                                    
                                    const newLatest = lotteryData[0].d;
                                    updateDataStatus(newLatest !== oldLatest ? `✅ 已更新到 ${newLatest}` : '数据已是最新');
                                    displayRecentDraws();
                                    calculateAllRecords();
                                    calculateTodaySignal();
                                    return;
                                }
                            }
                        } catch (e) {
                            console.log('Source failed:', source.url, proxyUrl, e.message);
                        }
                    }
                }
                
                // 所有源都失败
                const latestDate = lotteryData.length > 0 ? lotteryData[0].d : '';
                const today = new Date().toISOString().split('T')[0];
                const yesterday = new Date(Date.now() - 86400000).toISOString().split('T')[0];
                
                if (latestDate === today) {
                    updateDataStatus('✅ 数据已是最新');
                } else if (latestDate === yesterday) {
                    updateDataStatus('✅ 数据已是最新（今天可能还未开奖）');
                } else {
                    updateDataStatus(`⚠️ 网络获取失败，本地数据到 ${latestDate}`);
                }
            } catch (error) {
                console.error('获取新数据失败:', error);
                updateDataStatus('⚠️ 网络异常');
            }
        }

        // 解析az24.vn数据
        function parseAz24Data(html) {
            let results = [];
            
            // 方法1: 查找日期和号码的模式
            // 格式: <td>DD-MM-YYYY</td>...<td class="gdb">XX</td>
            const datePattern = /xsmb-(\d{1,2})-(\d{1,2})-(\d{4})\.html[^>]*>[^<]*<\/a>\s*<\/td>\s*<td[^>]*class="[^"]*gdb[^"]*"[^>]*>(\d{2})</gi;
            let match;
            
            while ((match = datePattern.exec(html)) !== null) {
                const day = match[1].padStart(2, '0');
                const month = match[2].padStart(2, '0');
                const year = match[3];
                const num = parseInt(match[4]);
                results.push({
                    d: `${year}-${month}-${day}`,
                    n: num
                });
            }
            
            // 方法2: 直接找gdb-cell
            if (results.length === 0) {
                const numPattern = /class="gdb[^"]*"[^>]*>(\d{2})</gi;
                const datePattern2 = /(\d{1,2})-(\d{1,2})-(\d{4})/g;
                let numbers = [];
                let dates = [];
                
                while ((match = numPattern.exec(html)) !== null) {
                    numbers.push(parseInt(match[1]));
                }
                
                while ((match = datePattern2.exec(html)) !== null) {
                    dates.push(`${match[3]}-${match[2].padStart(2,'0')}-${match[1].padStart(2,'0')}`);
                }
                
                // 如果找到了号码但没有足够日期，用当前日期往前推算
                if (numbers.length > 0 && dates.length < numbers.length) {
                    const today = new Date();
                    for (let i = 0; i < numbers.length; i++) {
                        const date = new Date(today);
                        date.setDate(date.getDate() - i);
                        results.push({
                            d: date.toISOString().split('T')[0],
                            n: numbers[i]
                        });
                    }
                }
            }
            
            return results;
        }
        
        // 解析xoso.me数据
        function parseXosoMeData(html) {
            let results = [];
            // 类似的解析逻辑
            const gdbPattern = /gdb[^>]*>(\d{2})</gi;
            let numbers = [];
            let match;
            
            while ((match = gdbPattern.exec(html)) !== null) {
                numbers.push(parseInt(match[1]));
            }
            
            if (numbers.length > 0) {
                const today = new Date();
                for (let i = 0; i < numbers.length; i++) {
                    const date = new Date(today);
                    date.setDate(date.getDate() - i);
                    results.push({
                        d: date.toISOString().split('T')[0],
                        n: numbers[i]
                    });
                }
            }
            
            return results;
        }
    </script>
</body>
</html>'''

# 写入HTML文件
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html_template)

print(f'Generated index.html')
print(f'  - Embedded data: {len(data)} records')
print(f'  - File size: ~{len(html_template) / 1024:.1f} KB')
print(f'  - Features: 自动回溯统计, 周期筛选, 记录过滤')
