"""
Fynix Systems - Autonomous Bookkeeping Orchestrator
====================================================
Central coordinator for the contractor bookkeeping agent network.
Routes tasks, monitors agent health, and ensures workflow completion.
"""

import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("FynixOrchestrator")


class TaskStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    REQUIRES_HUMAN = "requires_human"


class AgentType(Enum):
    INGESTION = "ingestion"
    CATEGORIZATION = "categorization"
    RECONCILIATION = "reconciliation"
    INVOICE = "invoice"
    PAYROLL = "payroll"
    REPORTING = "reporting"
    COMPLIANCE = "compliance"


@dataclass
class Task:
    """Represents a bookkeeping task to be processed by an agent."""
    task_id: str
    task_type: AgentType
    client_id: str
    payload: Dict[str, Any]
    status: TaskStatus = TaskStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3


@dataclass
class ClientProfile:
    """Contractor client profile with business context."""
    client_id: str
    business_name: str
    trade: str  # HVAC, Plumbing, Roofing, Electrical, General
    state: str
    chart_of_accounts: Dict[str, str]
    tax_classification: str  # S-Corp, LLC, Sole Prop
    payroll_frequency: str  # weekly, bi-weekly, monthly
    integration_credentials: Dict[str, str] = field(default_factory=dict)


class BookkeepingOrchestrator:
    """
    Central orchestrator for the autonomous bookkeeping system.
    
    Blue Ocean Differentiator: This isn't a tool that helps humans do bookkeeping.
    This IS the bookkeeper - an autonomous system that handles the full workflow.
    """
    
    def __init__(self):
        self.task_queue: asyncio.Queue = asyncio.Queue()
        self.active_tasks: Dict[str, Task] = {}
        self.completed_tasks: List[Task] = []
        self.clients: Dict[str, ClientProfile] = {}
        self.agents: Dict[AgentType, 'BaseAgent'] = {}
        self.running = False
        
    async def register_agent(self, agent_type: AgentType, agent: 'BaseAgent'):
        """Register a specialized agent with the orchestrator."""
        self.agents[agent_type] = agent
        logger.info(f"Registered agent: {agent_type.value}")
        
    async def register_client(self, client: ClientProfile):
        """Onboard a new contractor client."""
        self.clients[client.client_id] = client
        logger.info(f"Registered client: {client.business_name} ({client.trade})")
        
        # Trigger initial setup workflow
        await self.create_task(
            task_type=AgentType.INGESTION,
            client_id=client.client_id,
            payload={"action": "initial_sync", "source": "all"}
        )
        
    async def create_task(
        self, 
        task_type: AgentType, 
        client_id: str, 
        payload: Dict[str, Any]
    ) -> str:
        """Create a new task and add it to the processing queue."""
        task_id = f"{client_id}_{task_type.value}_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
        
        task = Task(
            task_id=task_id,
            task_type=task_type,
            client_id=client_id,
            payload=payload
        )
        
        self.active_tasks[task_id] = task
        await self.task_queue.put(task)
        
        logger.info(f"Created task: {task_id}")
        return task_id
        
    async def process_task(self, task: Task) -> Task:
        """Route task to appropriate agent and handle result."""
        task.status = TaskStatus.IN_PROGRESS
        
        try:
            agent = self.agents.get(task.task_type)
            if not agent:
                raise ValueError(f"No agent registered for {task.task_type.value}")
            
            # Execute the agent's processing
            result = await agent.process(task, self.clients.get(task.client_id))
            
            task.result = result
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.now()
            
            # Trigger downstream tasks based on result
            await self._handle_task_completion(task)
            
        except Exception as e:
            task.error = str(e)
            task.retry_count += 1
            
            if task.retry_count >= task.max_retries:
                task.status = TaskStatus.FAILED
                await self._escalate_to_human(task)
            else:
                task.status = TaskStatus.PENDING
                await self.task_queue.put(task)
                
        return task
        
    async def _handle_task_completion(self, task: Task):
        """
        Workflow routing logic - determines what happens after each task completes.
        This is the "intelligence" that makes the system autonomous.
        """
        workflow_map = {
            AgentType.INGESTION: [AgentType.CATEGORIZATION],
            AgentType.CATEGORIZATION: [AgentType.RECONCILIATION],
            AgentType.RECONCILIATION: [AgentType.REPORTING, AgentType.COMPLIANCE],
            AgentType.INVOICE: [AgentType.CATEGORIZATION],
            AgentType.PAYROLL: [AgentType.CATEGORIZATION, AgentType.COMPLIANCE],
        }
        
        next_agents = workflow_map.get(task.task_type, [])
        
        for next_agent_type in next_agents:
            await self.create_task(
                task_type=next_agent_type,
                client_id=task.client_id,
                payload={
                    "source_task": task.task_id,
                    "source_result": task.result
                }
            )
            
    async def _escalate_to_human(self, task: Task):
        """
        When AI can't resolve, create a human review ticket.
        Key insight: Track WHAT fails to improve agent training.
        """
        task.status = TaskStatus.REQUIRES_HUMAN
        
        escalation = {
            "task_id": task.task_id,
            "client_id": task.client_id,
            "task_type": task.task_type.value,
            "error": task.error,
            "payload": task.payload,
            "escalated_at": datetime.now().isoformat(),
            "resolution_required": True
        }
        
        logger.warning(f"Escalating to human: {json.dumps(escalation, indent=2)}")
        
        # In production: Send to Slack, create GHL task, email, etc.
        return escalation
        
    async def run(self):
        """Main processing loop."""
        self.running = True
        logger.info("Orchestrator started - processing tasks")
        
        while self.running:
            try:
                # Non-blocking get with timeout
                task = await asyncio.wait_for(
                    self.task_queue.get(), 
                    timeout=1.0
                )
                await self.process_task(task)
                
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"Processing error: {e}")
                
    async def stop(self):
        """Graceful shutdown."""
        self.running = False
        logger.info("Orchestrator stopping")
        
    def get_client_status(self, client_id: str) -> Dict[str, Any]:
        """Get current bookkeeping status for a client."""
        client_tasks = [
            t for t in list(self.active_tasks.values()) + self.completed_tasks
            if t.client_id == client_id
        ]
        
        return {
            "client_id": client_id,
            "pending_tasks": len([t for t in client_tasks if t.status == TaskStatus.PENDING]),
            "in_progress": len([t for t in client_tasks if t.status == TaskStatus.IN_PROGRESS]),
            "completed": len([t for t in client_tasks if t.status == TaskStatus.COMPLETED]),
            "failed": len([t for t in client_tasks if t.status == TaskStatus.FAILED]),
            "requires_human": len([t for t in client_tasks if t.status == TaskStatus.REQUIRES_HUMAN]),
            "last_activity": max([t.created_at for t in client_tasks], default=None)
        }


class BaseAgent:
    """Base class for all specialized bookkeeping agents."""
    
    def __init__(self, agent_type: AgentType):
        self.agent_type = agent_type
        self.logger = logging.getLogger(f"Agent_{agent_type.value}")
        
    async def process(self, task: Task, client: ClientProfile) -> Dict[str, Any]:
        """Override in subclasses to implement agent-specific logic."""
        raise NotImplementedError("Subclasses must implement process()")
        
    def _get_trade_specific_rules(self, trade: str) -> Dict[str, Any]:
        """
        Return trade-specific bookkeeping rules.
        This is where niche expertise gets encoded.
        """
        trade_rules = {
            "HVAC": {
                "common_categories": [
                    "refrigerant_purchases", "equipment_sales", 
                    "maintenance_contracts", "parts_inventory"
                ],
                "tax_considerations": ["section_179_equipment"],
                "compliance": ["epa_608_tracking"]
            },
            "Plumbing": {
                "common_categories": [
                    "fixtures", "pipe_materials", "permits",
                    "service_calls", "new_construction"
                ],
                "tax_considerations": ["material_cost_basis"],
                "compliance": ["license_renewal_tracking"]
            },
            "Roofing": {
                "common_categories": [
                    "materials_shingles", "materials_metal",
                    "labor_subcontract", "equipment_rental", "disposal_fees"
                ],
                "tax_considerations": ["progress_billing_recognition"],
                "compliance": ["workers_comp_audit_prep"]
            },
            "Electrical": {
                "common_categories": [
                    "wire_conduit", "fixtures_switches", 
                    "permits", "inspection_fees"
                ],
                "tax_considerations": ["apprentice_tax_credits"],
                "compliance": ["continuing_education_tracking"]
            },
            "General": {
                "common_categories": [
                    "materials", "labor", "subcontractors",
                    "permits", "equipment"
                ],
                "tax_considerations": ["standard"],
                "compliance": ["general_liability_tracking"]
            }
        }
        
        return trade_rules.get(trade, trade_rules["General"])


# Example usage and testing
if __name__ == "__main__":
    async def demo():
        orchestrator = BookkeepingOrchestrator()
        
        # Register a sample client
        sample_client = ClientProfile(
            client_id="hvac_001",
            business_name="Cool Comfort HVAC",
            trade="HVAC",
            state="GA",
            chart_of_accounts={
                "1000": "Checking",
                "1100": "Savings",
                "4000": "Service Revenue",
                "4100": "Installation Revenue",
                "5000": "Parts & Materials",
                "5100": "Refrigerant",
                "6000": "Labor"
            },
            tax_classification="S-Corp",
            payroll_frequency="bi-weekly"
        )
        
        await orchestrator.register_client(sample_client)
        
        # Check status
        status = orchestrator.get_client_status("hvac_001")
        print(f"Client status: {json.dumps(status, indent=2, default=str)}")
        
    asyncio.run(demo())
