"""
408专业课学习模块
- 四科知识框架
- 经典例题库
- AI讲题（用户贴题，LLM详细解答）
"""
import json
from pathlib import Path

from openai import OpenAI

from .chat_engine import client, MODEL

DATA_DIR = Path(__file__).parent.parent / "data"

def _load_questions() -> list[dict]:
    with open(DATA_DIR / "cs408_questions.json", encoding="utf-8") as f:
        return json.load(f)

QUESTIONS = _load_questions()

SUBJECTS = ["数据结构", "计算机组成原理", "操作系统", "数据库"]

# 四科知识框架（用于快速回顾）
KNOWLEDGE_MAP = {
    "数据结构": [
        "线性表：顺序表、链表（单/双/循环）",
        "栈与队列：顺序/链式、应用（括号匹配、表达式求值）",
        "树与二叉树：遍历、线索化、哈夫曼树、BST/AVL",
        "图：存储（邻接矩阵/表）、遍历（BFS/DFS）、最短路、最小生成树、拓扑排序",
        "查找：顺序、折半、B树/B+树、哈希表",
        "排序：插入/希尔/冒泡/快排/选择/堆排/归并/基数（时间空间稳定性）",
    ],
    "计算机组成原理": [
        "计算机系统概述：性能指标（CPI、MIPS、MFLOPS）",
        "数据表示：定点/浮点、IEEE754、校验码（奇偶/海明/CRC）",
        "存储器：层次结构、Cache（映射/替换/写策略）、虚拟存储器",
        "指令系统：寻址方式、CISC/RISC",
        "CPU：数据通路、控制器（硬布线/微程序）、流水线（冒险/加速比）",
        "总线与IO：总线事务、中断、DMA",
    ],
    "操作系统": [
        "进程：状态转换、PCB、进程 vs 线程",
        "处理机调度：FCFS/SJF/RR/多级反馈队列、周转时间/带权周转",
        "同步互斥：PV操作、生产者消费者、读者写者、哲学家进餐",
        "死锁：四个必要条件、预防/避免（银行家算法）",
        "内存管理：连续分配、分页/分段、虚拟内存（页面置换OPT/FIFO/LRU）",
        "文件系统：目录、物理结构、空闲块管理",
        "IO管理：缓冲、SPOOLing、设备分配",
    ],
    "数据库": [
        "关系模型：实体完整性、参照完整性、用户定义完整性",
        "关系代数：σ选择、π投影、⋈连接、÷除",
        "SQL：DDL/DML/DCL、连接查询、嵌套查询、聚集函数",
        "范式：1NF→2NF→3NF→BCNF，函数依赖、候选键求解",
        "事务ACID：原子性、一致性、隔离性、持久性",
        "并发控制：封锁（S/X锁）、两段锁协议、死锁",
    ],
}

def explain_question(question_text: str, subject: str = "未知") -> str:
    """调用LLM，把用户贴的题详细讲一遍。"""
    prompt = f"""你是408考研辅导老师。请详细讲解下面这道题。
科目：{subject}

题目：
{question_text}

请按以下结构输出：
1. 【考点】这题考什么知识点
2. 【思路】一步步怎么想
3. 【答案】最终结果
4. 【易错点】考生常错在哪
5. 【举一反三】类似题怎么做

要具体、清楚，像一对一辅导，不要套话。"""

    resp = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=1500,
    )
    return resp.choices[0].message.content
