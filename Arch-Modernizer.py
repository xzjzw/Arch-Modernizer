#!/usr/bin/env python3
"""
Arch-Modernizer Agent Demo
用于演示多 Agent 协作重构遗留代码的核心逻辑
"""

import os
import re
import json
import time
import subprocess
from datetime import datetime
from typing import Dict, List, Tuple, Optional

class MockLLM:
    def __init__(self):
        self.total_tokens = 0
    
    def chat(self, prompt: str, max_tokens: int = 500) -> str:
        """ LLM 响应，同时计算 token 消耗"""
              prompt_tokens = len(prompt) // 4
        response_tokens = max_tokens
        self.total_tokens += prompt_tokens + response_tokens
        
        # 返回重构建议
        if "analyze dependencies" in prompt.lower():
            return self._planning_response()
        elif "convert" in prompt.lower():
            return self._conversion_response()
        else:
            return '{"action": "no_change", "confidence": 0.9}'
    
    def _planning_response(self) -> str:
        return """{
    "plan": [
        {"phase": 1, "target": "utils/helpers.js", "risk": "low", "estimated_tokens": 5000},
        {"phase": 2, "target": "services/api.js", "risk": "medium", "estimated_tokens": 15000},
        {"phase": 3, "target": "controllers/main.js", "risk": "high", "estimated_tokens": 25000}
    ],
    "reasoning": "Utils layer has no external dependencies, safe to start. API services depend on utils but have few consumers. Controllers have highest risk due to 34 dependents."
}"""
    
    def _conversion_response(self) -> str:
        return """{
    "changes": [
        {"line": 15, "original": "$scope.data = response.data;", "new": "setData(response.data);"},
        {"line": 23, "original": "$http.get('/api/users')", "new": "fetch('/api/users')"},
        {"line": 45, "original": "$q.defer()", "new": "new Promise()"}
    ],
    "new_tests": [
        "test_async_data_fetch",
        "test_error_handling"
    ]
}"""


class ArchModernizer:
    """Arch-Modernizer 主类 - 多 Agent 协作重构系统"""
    
    def __init__(self, project_path: str):
        self.project_path = project_path
        self.llm = MockLLM()
        self.plan = []
        self.results = {
            "success": [],
            "failed": [],
            "total_tokens": 0,
            "tests_passed": 0,
            "tests_failed": 0
        }
    
    def log(self, agent_name: str, message: str, level: str = "INFO"):
        """统一日志输出"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] [{agent_name}] [{level}] {message}")
    
    def scan_codebase(self) -> Dict:
        """Agent 1: 洞察与规划 Agent - 扫描代码库并生成依赖图谱"""
        self.log("Planner", "开始扫描代码库...")
        
        # 扫描 文件
        files_found = 247
        self.log("Planner", f"扫描完成，发现 {files_found} 个文件")
        
        # 长链推理：计算风险分数
        self.log("Planner", "执行长链推理 - 计算模块风险分数...")
        
        # 依赖分析结果
        analysis = {
            "total_files": files_found,
            "high_risk_modules": [
                {"name": "src/core/auth.js", "dependents": 34, "complexity": 8.2},
                {"name": "src/payment/main.js", "dependents": 12, "complexity": 9.4},
            ],
            "low_risk_modules": [
                {"name": "src/utils/helpers.js", "dependents": 0, "complexity": 3.1},
                {"name": "src/utils/date.js", "dependents": 2, "complexity": 2.5},
            ]
        }
        
        self.log("Planner", f"高风险模块: {analysis['high_risk_modules'][0]['name']} (被依赖 {analysis['high_risk_modules'][0]['dependents']} 次)")
        
        return analysis
    
    def generate_plan(self, analysis: Dict) -> List:
        """基于长链推理生成重构计划"""
        self.log("Planner", "生成重构计划中...")
        
        # 调用 LLM 进行规划
        prompt = f"Analyze dependencies and generate refactor plan: {json.dumps(analysis)}"
        response = self.llm.chat(prompt)
        
        plan_data = json.loads(response)
        self.plan = plan_data.get("plan", [])
        
        for phase in self.plan:
            self.log("Planner", f"阶段 {phase['phase']}: 重构 {phase['target']} (风险: {phase['risk']}, 预估 Token: {phase['estimated_tokens']})")
        
        return self.plan
    
    def execute_refactor(self, phase: Dict) -> Dict:
        """Agent 2: 重构执行 Agent - 执行具体的代码转换"""
        self.log("Executor", f"开始重构 {phase['target']}...")
        
        # 读取文件内容
        mock_file_content = """
        angular.module('app').controller('MainCtrl', function($scope, $http, $q) {
            $scope.users = [];
            $http.get('/api/users').then(function(response) {
                $scope.users = response.data;
            });
            
            $scope.save = function() {
                var deferred = $q.defer();
                // 保存逻辑
                deferred.resolve();
                return deferred.promise;
            };
        });
        """
        
        # 调用 LLM 进行转换
        prompt = f"Convert AngularJS code to React. Target file: {phase['target']}\nCode:\n{mock_file_content}"
        response = self.llm.chat(prompt, max_tokens=800)
        conversion = json.loads(response)
        
        changes_made = len(conversion.get("changes", []))
        self.log("Executor", f"完成 {changes_made} 处代码转换")
        
        return {
            "file": phase['target'],
            "changes": conversion.get("changes", []),
            "new_tests": conversion.get("new_tests", [])
        }
    
    def run_tests(self, refactor_result: Dict) -> Tuple[bool, str]:
        """Agent 3: 验证与自我纠错 Agent - 运行测试并处理失败"""
        self.log("Validator", f"运行单元测试: {refactor_result['file']}")
        
        # 测试结果（80% 概率成功，用于演示自我纠错）
        import random
        test_passed = random.random() > 0.3  # 70% 通过率用于演示纠错
        
        if test_passed:
            self.log("Validator", f"✅ 所有测试通过！新增 {len(refactor_result.get('new_tests', []))} 个测试用例")
            self.results["tests_passed"] += 1
            return True, "All tests passed"
        else:
            self.log("Validator", "❌ 测试失败，进入自我纠错流程", "ERROR")
            return self.self_correction(refactor_result)
    
    def self_correction(self, refactor_result: Dict, max_retries: int = 3) -> Tuple[bool, str]:
        """自我纠错循环 - 尝试修复失败的测试"""
        for attempt in range(1, max_retries + 1):
            self.log("SelfCorrection", f"尝试 {attempt}/{max_retries} - 分析错误并修复...")
            
            # 错误分析
            error_msg = "TypeError: Cannot read property 'then' of undefined at line 23"
            self.log("SelfCorrection", f"错误追踪: {error_msg}")
            
            # 提出修复假设
            hypotheses = [
                "缺少 async/await 包装",
                "Promise 未正确返回",
                "变量名未同步"
            ]
            hypothesis = hypotheses[attempt - 1]
            self.log("SelfCorrection", f"修复假设: {hypothesis}")
            
            # 修复操作
            time.sleep(0.5)             
            # 重新运行测试（ 60% 修复成功率）
            fix_success = attempt == 2  # 第二次尝试成功
            if fix_success:
                self.log("SelfCorrection", f"✅ 修复成功！测试通过")
                return True, f"Fixed after {attempt} attempt(s)"
        
        self.log("SelfCorrection", f"❌ {max_retries} 次尝试后仍失败，回滚变更", "ERROR")
        return False, "Failed after max retries, rolled back"
    
    def generate_report(self) -> str:
        """Agent 4: 报告生成 Agent - 生成 PR 摘要"""
        self.log("Reporter", "生成重构报告...")
        
        report = f"""
# Arch-Modernizer 重构报告

## 执行摘要
- 重构文件数: {len(self.results['success'])} 成功 / {len(self.results['failed'])} 失败
- 新增测试用例: {self.results['tests_passed']} 个通过验证
- Token 消耗: {self.results['total_tokens']:,}
- 预估成本: ${self.results['total_tokens'] * 0.000002:.4f}

## 成功重构的文件
{chr(10).join(['- ' + f for f in self.results['success']]) if self.results['success'] else '- 无'}

## 需人工介入的文件
{chr(10).join(['- ' + f for f in self.results['failed']]) if self.results['failed'] else '- 无'}

## 重点关注建议
1. 请确认 utils/helpers.js 中的时区处理逻辑
2. 验证 API 调用的错误处理是否符合团队规范
3. 检查新生成的测试用例是否正确覆盖边界条件

---
*报告生成时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}*
*Agent 版本: Arch-Modernizer v1.0*
"""
        self.log("Reporter", f"报告已生成，共 {len(report)} 字符")
        return report
    
    def run(self) -> Dict:
        """主运行流程 - 串联所有 Agent"""
        self.log("System", "🚀 Arch-Modernizer Agent 启动")
        
        # Step 1: 扫描与规划
        analysis = self.scan_codebase()
        plan = self.generate_plan(analysis)
        
        # Step 2-3: 循环执行每个阶段的重构
        for phase in plan:
            self.log("System", f"{'='*50}")
            
            # 执行重构
            refactor_result = self.execute_refactor(phase)
            
            # 验证与自我纠错
            success, message = self.run_tests(refactor_result)
            
            if success:
                self.results["success"].append(phase['target'])
            else:
                self.results["failed"].append(phase['target'])
            
            # 累计 token
            self.results["total_tokens"] += self.llm.total_tokens
        
        # Step 4: 生成报告
        report = self.generate_report()
        
        # 保存报告到文件
        report_file = f"refactor_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        with open(report_file, 'w') as f:
            f.write(report)
        self.log("System", f"报告已保存至: {report_file}")
        
        # 最终统计
        self.log("System", f"{'='*50}")
        self.log("System", f"✅ 重构完成！成功: {len(self.results['success'])} 个文件，失败: {len(self.results['failed'])} 个文件")
        self.log("System", f"💰 Token 消耗: {self.results['total_tokens']:,} (约 ${self.results['total_tokens'] * 0.000002:.2f})")
        
        return self.results


def main():
    """演示入口"""
    print("""
    ╔══════════════════════════════════════════════════════════════╗
    ║         Arch-Modernizer - 多 Agent 遗留代码重构系统          ║
    ║                                               ║
    ╚══════════════════════════════════════════════════════════════╝
    """)
    
    # 初始化 Agent
    agent = ArchModernizer(project_path="./legacy_codebase")
    
    # 运行重构流程
    results = agent.run()
    
    print("\n" + "="*60)
    print("运行完成！请查看生成的 refactor_report_*.md 文件获取详细报告")
    print("="*60)


if __name__ == "__main__":
    main()
