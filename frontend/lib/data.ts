import { DEMO_MATTER_ID } from "@/lib/routes";
import type { ChatMessage, CitationRef, EvidenceItem, GraphEdge, GraphNode, MatterSummary } from "@/lib/types";

export const currentMatter: MatterSummary = {
  id: DEMO_MATTER_ID,
  title: "试用期解除与赔偿风险评估",
  matterType: "labor",
  jurisdiction: "中国大陆 / 上海",
  status: "in_review",
  summary: "员工在试用期内因绩效与岗位匹配争议被解除，需要评估解除依据、证据链与潜在赔偿风险。",
  updatedAt: "今天 10:18",
};

export const matters: MatterSummary[] = [
  currentMatter,
  {
    id: "contract-review",
    title: "SaaS 服务协议责任限制审查",
    matterType: "contract",
    jurisdiction: "中国大陆 / 北京",
    status: "draft",
    summary: "审查标准服务协议中的间接损失、数据安全与服务可用性条款。",
    updatedAt: "昨天 16:42",
  },
  {
    id: "equity-incentive",
    title: "早期团队股权激励退出安排",
    matterType: "corporate",
    jurisdiction: "中国大陆 / 深圳",
    status: "verified",
    summary: "梳理员工期权授予、离职回购和成熟期条款的合规与商业风险。",
    updatedAt: "4 月 21 日",
  },
  {
    id: "privacy-compliance",
    title: "用户画像功能个人信息合规",
    matterType: "compliance",
    jurisdiction: "中国大陆",
    status: "partial",
    summary: "评估画像标签、自动化决策提示与最小必要原则下的数据处理边界。",
    updatedAt: "4 月 18 日",
  },
];

export const citations: CitationRef[] = [
  { id: "c1", type: "law", label: "劳动合同法第 39 条", sourceId: "e1" },
  { id: "c2", type: "case", label: "上海二中院劳动争议案例", sourceId: "e2" },
  { id: "c3", type: "excerpt", label: "绩效沟通记录摘要", sourceId: "e3" },
];

export const messages: ChatMessage[] = [
  {
    id: "m1",
    role: "system",
    content: "事项已建立。系统将先识别劳动争议路径，再检索法律依据、案例与内部证据。",
    createdAt: "10:12",
  },
  {
    id: "m2",
    role: "user",
    content: "员工试用期第 5 个月，部门认为不符合录用条件，HR 想本周解除。现有材料包括面试评分、岗位说明和两次绩效沟通。",
    createdAt: "10:14",
  },
  {
    id: "m3",
    role: "assistant",
    content:
      "初步判断解除路径需要严格绑定“不符合录用条件”及其事先明确性。当前证据中，岗位说明和绩效沟通记录有支持价值，但还需要确认录用条件是否在入职前或入职时明示，并能对应到具体不达标事实。",
    createdAt: "10:16",
    citations,
  },
  {
    id: "m4",
    role: "agent_event",
    content: "检索代理已找到 3 条高相关依据，风险审查代理标记 1 项高不确定性。",
    createdAt: "10:17",
  },
];

export const evidenceItems: EvidenceItem[] = [
  {
    id: "e1",
    type: "statute",
    title: "中华人民共和国劳动合同法 第三十九条",
    authority: "全国人民代表大会常务委员会",
    date: "2012-12-28",
    jurisdiction: "中国大陆",
    excerpt:
      "劳动者在试用期间被证明不符合录用条件的，用人单位可以解除劳动合同。关键在于录用条件的明确告知、证明责任和解除程序的完整性。",
    relevanceScore: 0.94,
    relatedIssues: ["解除依据", "证明责任"],
  },
  {
    id: "e2",
    type: "case",
    title: "试用期录用条件争议二审判例",
    authority: "上海市第二中级人民法院",
    date: "2023-08-11",
    jurisdiction: "上海",
    excerpt:
      "法院重点审查录用条件是否具体、是否已向劳动者明示，以及考核结论与录用条件之间是否存在可验证对应关系。",
    relevanceScore: 0.88,
    relatedIssues: ["录用条件明示", "考核对应性"],
  },
  {
    id: "e3",
    type: "memo",
    title: "绩效沟通记录与岗位说明摘要",
    authority: "客户提交材料",
    date: "2026-04-22",
    jurisdiction: "上海",
    excerpt:
      "两次沟通均记录交付延期与协作反馈，但未直接引用入职确认的录用条件。建议补充入职签收、岗位目标确认与考核规则送达证据。",
    relevanceScore: 0.81,
    relatedIssues: ["事实证据", "程序风险"],
  },
];

export const agentEvents = [
  { name: "Intake agent", status: "completed", elapsed: "02s", message: "识别为劳动合同解除事项" },
  { name: "Planner agent", status: "completed", elapsed: "05s", message: "拆解为录用条件、证据链、程序与赔偿风险" },
  { name: "Retriever agent", status: "completed", elapsed: "11s", message: "检索法律、案例与提交材料" },
  { name: "Reasoner agent", status: "active", elapsed: "18s", message: "生成结构化答复草稿" },
  { name: "Review agent", status: "queued", elapsed: "-", message: "等待风险复核" },
];

export const analysisSections = [
  {
    title: "事实时间线",
    body: "入职时签署劳动合同；试用期第 3 与第 5 个月发生绩效沟通；部门拟以不符合录用条件解除。",
    meta: "3 条证据支持",
  },
  {
    title: "核心法律问题",
    body: "录用条件是否明确、已明示，考核事实是否可证明，以及解除通知和工会程序是否完整。",
    meta: "高优先级",
  },
  {
    title: "适用依据",
    body: "劳动合同法第三十九条可作为解除基础，但证明标准通常高于普通绩效不佳表述。",
    meta: "2 条权威依据",
  },
  {
    title: "初步结论",
    body: "若无法证明录用条件的事先明示，直接解除存在违法解除风险。建议先补强证据链并准备替代协商方案。",
    meta: "需复核",
  },
];

export const graphNodes: GraphNode[] = [
  { id: "issue", label: "试用期解除争议", type: "issue", summary: "事项焦点与风险聚合节点", x: 48, y: 46 },
  { id: "law39", label: "劳动合同法 39 条", type: "law", summary: "试用期解除的主要法条依据", x: 23, y: 25 },
  { id: "case-sh", label: "上海二中院案例", type: "case", summary: "录用条件明示与考核对应性审查", x: 72, y: 24 },
  { id: "condition", label: "录用条件明示", type: "behavior", summary: "入职前后是否明确告知具体条件", x: 31, y: 72 },
  { id: "burden", label: "用人单位举证责任", type: "responsibility", summary: "证明不符合录用条件的责任主体", x: 71, y: 70 },
];

export const graphEdges: GraphEdge[] = [
  { id: "g1", from: "issue", to: "law39", label: "适用" },
  { id: "g2", from: "issue", to: "case-sh", label: "参照" },
  { id: "g3", from: "law39", to: "condition", label: "要求" },
  { id: "g4", from: "case-sh", to: "burden", label: "强调" },
  { id: "g5", from: "condition", to: "burden", label: "证明" },
];

export const adminMetrics = [
  { label: "知识库新鲜度", value: "92%", detail: "最近同步 18 分钟前" },
  { label: "图谱覆盖", value: "18.4k", detail: "法律实体与关系" },
  { label: "检索延迟", value: "740ms", detail: "P95 混合检索" },
  { label: "失败任务", value: "2", detail: "等待重新入队" },
];
