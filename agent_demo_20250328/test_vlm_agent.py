# test_vlm_agent.py
# 测试vlm_agent_go.py的Agent编排功能

print('测试VLM+Agent编排系统\n')

from utils_agent import *

# 初始化对话历史
message = []
message.append({"role": "system", "content": AGENT_SYS_PROMPT})

# 测试指令
test_orders = [
    "先归零，再移动到小人的位置，然后摇头",
    "找到桌上的玩具车，移动到那里",
    "先归零，然后用视觉识别桌上的红色方块，最后点头",
    "帮我把绿色方块放在小猪佩奇上",
]

print('=== 测试Agent编排 ===\n')

for idx, order in enumerate(test_orders, 1):
    print(f'\n【测试 {idx}】')
    print(f'用户指令: {order}')
    
    # 添加用户消息
    test_message = message.copy()
    test_message.append({"role": "user", "content": order})
    
    # 调用Agent编排
    try:
        result = agent_plan(test_message, model='360')
        print(f'Agent输出: {result}')
        
        # 解析结果
        import ast
        plan = ast.literal_eval(result)
        print(f'  函数列表: {plan.get("function", [])}')
        print(f'  回复内容: {plan.get("response", "")}')
        
    except Exception as e:
        print(f'  ❌ 错误: {e}')
    
    print('-' * 60)

print('\n✅ 测试完成！')
