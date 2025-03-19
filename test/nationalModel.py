import mesa
import numpy as np
from mesa.time import RandomActivation
from mesa.space import MultiGrid

# 中央政府智能体类
class CentralGovernment(mesa.Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.reproductive_subsidy = 1000  # 生育补贴标准
        self.retirement_age = 65  # 退休年龄
        self.transfer_ratio = 0.1  # 财政转移支付比例

    def step(self):
        pass

# 地方政府智能体类
class LocalGovernment(mesa.Agent):
    def __init__(self, unique_id, model, region):
        super().__init__(unique_id, model)
        self.region = region
        self.extra_subsidy = 500  # 额外补贴
        self.fiscal_income = 0
        self.fiscal_expenditure = 0

    def step(self):
        # 执行中央政策并附加地方性措施
        pass

# 居民智能体类
class Resident(mesa.Agent):
    def __init__(self, unique_id, model, region):
        super().__init__(unique_id, model)
        self.region = region
        self.salary = np.random.randint(2000, 8000)

    def step(self):
        # 跨区域迁移决策
        regions = self.model.regions
        current_region = self.region
        for region in regions:
            if region != current_region:
                wj = self.model.get_average_wage(region)
                wi = self.model.get_average_wage(current_region)
                k = 0.1  # 迁移敏感系数
                migration_prob = k * (wj - wi) / wi
                if np.random.random() < migration_prob:
                    self.region = region
                    self.model.move_resident(self, current_region, region)

# 企业智能体类
class Enterprise(mesa.Agent):
    def __init__(self, unique_id, model, region):
        super().__init__(unique_id, model)
        self.region = region
        self.labor_cost = self.model.get_average_wage(region)
        self.recruitment_strategy = 10  # 初始招聘策略

    def step(self):
        # 根据区域劳动力成本调整招聘策略
        current_labor_cost = self.model.get_average_wage(self.region)
        if current_labor_cost > self.labor_cost:
            self.recruitment_strategy -= 1
        elif current_labor_cost < self.labor_cost:
            self.recruitment_strategy += 1
        self.labor_cost = current_labor_cost

# 模型类
class NationalModel(mesa.Model):
    def __init__(self, num_regions, num_residents, num_enterprises):
        self.num_regions = num_regions
        self.schedule = RandomActivation(self)
        self.grid = MultiGrid(10, 10, torus=True)
        self.regions = list(range(num_regions))
        self.residents = []
        self.enterprises = []

        # 创建中央政府智能体
        self.central_government = CentralGovernment(0, self)
        self.schedule.add(self.central_government)

        # 创建地方政府智能体
        for i in range(num_regions):
            local_gov = LocalGovernment(i + 1, self, i)
            self.schedule.add(local_gov)

        # 创建居民智能体
        for i in range(num_residents):
            region = np.random.choice(self.regions)
            resident = Resident(i + num_regions + 1, self, region)
            self.residents.append(resident)
            self.schedule.add(resident)

        # 创建企业智能体
        for i in range(num_enterprises):
            region = np.random.choice(self.regions)
            enterprise = Enterprise(i + num_regions + num_residents + 1, self, region)
            self.enterprises.append(enterprise)
            self.schedule.add(enterprise)

    def get_average_wage(self, region):
        residents_in_region = [r for r in self.residents if r.region == region]
        if len(residents_in_region) == 0:
            return 0
        total_salary = sum([r.salary for r in residents_in_region])
        return total_salary / len(residents_in_region)

    def move_resident(self, resident, from_region, to_region):
        # 处理居民迁移的逻辑
        pass

    def calculate_labor_flow(self):
        # 计算劳动力流动
        for i in self.regions:
            for j in self.regions:
                if i != j:
                    wi = self.get_average_wage(i)
                    wj = self.get_average_wage(j)
                    Li = len([r for r in self.residents if r.region == i])
                    k = 0.1
                    Mi_j = k * (wj - wi) / wi * Li
                    print(f"从区域 {i} 到区域 {j} 的迁移人口: {Mi_j}")

    def calculate_fiscal_transfer(self):
        # 计算财政转移支付
        central_gov = self.central_government
        for i in self.regions:
            for j in self.regions:
                if i != j:
                    GDPi = np.random.randint(10000, 50000)
                    GDPj = np.random.randint(10000, 50000)
                    transfer = central_gov.transfer_ratio * (GDPi - GDPj)
                    print(f"从区域 {i} 到区域 {j} 的财政转移支付: {transfer}")

    def step(self):
        self.schedule.step()
        self.calculate_labor_flow()
        self.calculate_fiscal_transfer()

# 创建模型实例并运行模拟
model = NationalModel(num_regions=3, num_residents=100, num_enterprises=20)
for _ in range(10):
    model.step()
    