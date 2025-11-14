"""
Real-World Multi-Domain Workflow Example

This example demonstrates a complete multi-domain workflow spanning:
BNI (Auth) → BNP (Services) → AXIS (Architecture) → IV (Innovation)

Scenario: Innovation Project Approval Workflow
1. Developer authenticates via BNI
2. Creates innovation project in IV
3. IV requests resource allocation from BNP
4. AXIS validates architectural compliance
5. BNP processes resource allocation
6. All steps tracked by governance

This shows real-world cross-domain collaboration.
"""

import asyncio
import sys
import uuid
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.governance.governance_manager import GovernanceManager  # noqa: E402
from src.core.event_bus import Event, EventBus  # noqa: E402
from src.core.state_manager import StateManager  # noqa: E402
from src.utils.metrics import MetricsCollector  # noqa: E402


class WorkflowOrchestrator:
    """Orchestrates multi-domain workflows."""

    def __init__(
        self,
        event_bus: EventBus,
        state_manager: StateManager,
        metrics: MetricsCollector,
    ):
        """Initialize workflow orchestrator."""
        self.event_bus = event_bus
        self.state_manager = state_manager
        self.metrics = metrics
        self.workflows = {}

        # Subscribe to workflow events
        self.event_bus.subscribe("workflow.start", self._handle_workflow_start)
        self.event_bus.subscribe("workflow.step.complete", self._handle_step_complete)

    async def _handle_workflow_start(self, event: Event) -> None:
        """Handle workflow start."""
        workflow_id = event.data["workflow_id"]
        workflow_type = event.data["workflow_type"]

        print(f"\n🔄 Starting workflow: {workflow_id}")
        print(f"   Type: {workflow_type}")

        self.workflows[workflow_id] = {
            "id": workflow_id,
            "type": workflow_type,
            "status": "in_progress",
            "steps_completed": [],
            "started_at": datetime.now().isoformat(),
        }

        # Save workflow state
        await self.state_manager.set_value(
            "PIPE", f"workflow_{workflow_id}", self.workflows[workflow_id]
        )

    async def _handle_step_complete(self, event: Event) -> None:
        """Handle workflow step completion."""
        workflow_id = event.data["workflow_id"]
        step = event.data["step"]
        result = event.data["result"]

        if workflow_id in self.workflows:
            self.workflows[workflow_id]["steps_completed"].append(
                {
                    "step": step,
                    "result": result,
                    "completed_at": datetime.now().isoformat(),
                }
            )

            print(f"   ✓ Step completed: {step}")

            # Update state
            await self.state_manager.set_value(
                "PIPE", f"workflow_{workflow_id}", self.workflows[workflow_id]
            )


async def innovation_project_workflow():
    """
    Demonstrate complete innovation project approval workflow.

    Flow:
    1. BNI: Authenticate developer
    2. IV: Create innovation project
    3. BNP: Check budget availability
    4. AXIS: Validate architecture compliance
    5. BNP: Allocate resources
    6. IV: Approve and start project
    """
    print("=" * 80)
    print("Multi-Domain Workflow: Innovation Project Approval")
    print("=" * 80)

    # Initialize
    event_bus = EventBus()
    state_manager = StateManager("./state/examples")
    metrics = MetricsCollector()
    governance = GovernanceManager()
    orchestrator = WorkflowOrchestrator(event_bus, state_manager, metrics)

    # Step 0: Setup domains and integrations
    print("\n📋 Setup: Registering domains and integrations...")

    domains = {
        "BNI": ["authentication", "user_management"],
        "IV": ["innovation_projects", "venture_tracking"],
        "BNP": ["resource_allocation", "budgeting", "financial_services"],
        "AXIS": ["architecture_validation", "compliance_checking"],
    }

    for domain, caps in domains.items():
        await governance.register_domain(domain, caps)

    # Create integrations
    integration_pairs = [
        ("IV", "BNI"),  # IV needs auth
        ("IV", "BNP"),  # IV needs resources
        ("IV", "AXIS"),  # IV needs arch validation
        ("BNP", "AXIS"),  # BNP needs compliance checks
    ]

    for source, target in integration_pairs:
        result = await governance.request_integration(
            source, target, "api", f"{source} to {target} integration", "high"
        )
        # Auto-approve for demo
        governance.review_pipeline.assign_reviewers(
            result["review_id"], ["reviewer@pipe.com"]
        )
        governance.review_pipeline.approve_review(
            result["review_id"], "reviewer@pipe.com"
        )
        await governance.approve_integration(result["integration_id"], "admin@pipe.com")

    print(f"   ✓ Registered {len(domains)} domains")
    print(f"   ✓ Created {len(integration_pairs)} integrations")

    # Generate workflow ID
    workflow_id = str(uuid.uuid4())[:8]

    # Start workflow
    await event_bus.publish(
        Event(
            event_type="workflow.start",
            source="PIPE",
            data={
                "workflow_id": workflow_id,
                "workflow_type": "innovation_project_approval",
            },
        )
    )

    print("\n🚀 Starting Innovation Project Approval Workflow")
    print(f"   Workflow ID: {workflow_id}")
    print("=" * 80)

    # ===== STEP 1: Authentication =====
    print("\n[STEP 1] Developer Authentication via BNI")
    print("-" * 80)

    developer = {
        "username": "alice.smith@iv.com",
        "employee_id": "EMP-1234",
        "department": "Innovation",
    }

    print(f"   Developer: {developer['username']}")
    print(f"   Department: {developer['department']}")

    await event_bus.publish(
        Event(
            event_type="auth.request",
            source="IV",
            data={
                "username": developer["username"],
                "password_hash": "secure_hash_12345",
                "workflow_id": workflow_id,
            },
        )
    )

    # Simulate BNI auth response
    auth_token = f"token_{uuid.uuid4().hex[:16]}"
    print("   ✓ Authentication successful")
    print(f"   Token: {auth_token[:20]}...")

    await event_bus.publish(
        Event(
            event_type="workflow.step.complete",
            source="BNI",
            data={
                "workflow_id": workflow_id,
                "step": "authentication",
                "result": "success",
            },
        )
    )

    await asyncio.sleep(0.5)

    # ===== STEP 2: Create Innovation Project =====
    print("\n[STEP 2] Create Innovation Project in IV")
    print("-" * 80)

    project = {
        "id": f"PROJ-{uuid.uuid4().hex[:8].upper()}",
        "name": "AI-Powered Customer Analytics Platform",
        "description": "Build ML platform for customer behavior analysis",
        "estimated_budget": 250000,
        "duration_months": 6,
        "team_size": 5,
        "technologies": ["Python", "TensorFlow", "Kubernetes", "PostgreSQL"],
        "created_by": developer["username"],
    }

    print(f"   Project ID: {project['id']}")
    print(f"   Name: {project['name']}")
    print(f"   Budget: ${project['estimated_budget']:,}")
    print(f"   Duration: {project['duration_months']} months")
    print(f"   Team Size: {project['team_size']} engineers")

    await event_bus.publish(
        Event(
            event_type="project.created",
            source="IV",
            data={"project": project, "workflow_id": workflow_id},
        )
    )

    await event_bus.publish(
        Event(
            event_type="workflow.step.complete",
            source="IV",
            data={
                "workflow_id": workflow_id,
                "step": "project_creation",
                "result": "success",
            },
        )
    )

    await asyncio.sleep(0.5)

    # ===== STEP 3: Budget Check via BNP =====
    print("\n[STEP 3] Budget Availability Check via BNP")
    print("-" * 80)

    print(f"   Checking budget availability for ${project['estimated_budget']:,}...")

    # Simulate budget check
    department_budget = {
        "department": "Innovation",
        "total_budget": 1000000,
        "allocated": 550000,
        "available": 450000,
    }

    is_budget_available = department_budget["available"] >= project["estimated_budget"]

    print(f"   Department Budget: ${department_budget['total_budget']:,}")
    print(f"   Already Allocated: ${department_budget['allocated']:,}")
    print(f"   Available: ${department_budget['available']:,}")

    if is_budget_available:
        print("   ✓ Budget available for project")
    else:
        print("   ✗ Insufficient budget")

    await event_bus.publish(
        Event(
            event_type="workflow.step.complete",
            source="BNP",
            data={
                "workflow_id": workflow_id,
                "step": "budget_check",
                "result": "approved" if is_budget_available else "rejected",
            },
        )
    )

    await asyncio.sleep(0.5)

    # ===== STEP 4: Architecture Validation via AXIS =====
    print("\n[STEP 4] Architecture Compliance Validation via AXIS")
    print("-" * 80)

    print("   Validating architecture compliance...")
    print(f"   Technologies: {', '.join(project['technologies'])}")

    # Simulate architecture validation
    arch_compliance = {
        "approved_technologies": project["technologies"],
        "security_scan": "passed",
        "scalability_review": "passed",
        "compliance_standards": ["GDPR", "SOC2"],
        "infrastructure": "Kubernetes approved",
    }

    print(f"   ✓ Security scan: {arch_compliance['security_scan']}")
    print(f"   ✓ Scalability: {arch_compliance['scalability_review']}")
    print(f"   ✓ Compliance: {', '.join(arch_compliance['compliance_standards'])}")
    print(f"   ✓ Infrastructure: {arch_compliance['infrastructure']}")

    await event_bus.publish(
        Event(
            event_type="workflow.step.complete",
            source="AXIS",
            data={
                "workflow_id": workflow_id,
                "step": "architecture_validation",
                "result": "approved",
            },
        )
    )

    await asyncio.sleep(0.5)

    # ===== STEP 5: Resource Allocation via BNP =====
    print("\n[STEP 5] Resource Allocation via BNP")
    print("-" * 80)

    allocated_resources = {
        "budget_allocated": project["estimated_budget"],
        "cost_center": "CC-INNOVATION-2025",
        "approval_level": "VP-LEVEL",
        "billing_cycle": "monthly",
        "headcount": project["team_size"],
        "infrastructure_tier": "Enterprise",
    }

    print(f"   ✓ Budget allocated: ${allocated_resources['budget_allocated']:,}")
    print(f"   ✓ Cost center: {allocated_resources['cost_center']}")
    print(f"   ✓ Headcount approved: {allocated_resources['headcount']} engineers")
    print(f"   ✓ Infrastructure: {allocated_resources['infrastructure_tier']}")

    await event_bus.publish(
        Event(
            event_type="workflow.step.complete",
            source="BNP",
            data={
                "workflow_id": workflow_id,
                "step": "resource_allocation",
                "result": "allocated",
            },
        )
    )

    await asyncio.sleep(0.5)

    # ===== STEP 6: Final Project Approval =====
    print("\n[STEP 6] Final Project Approval & Activation")
    print("-" * 80)

    final_approval = {
        "project_id": project["id"],
        "status": "APPROVED",
        "approved_by": "VP-Innovation",
        "approved_at": datetime.now().isoformat(),
        "start_date": "2025-12-01",
        "milestones": [
            {"phase": "Planning", "duration": "2 weeks"},
            {"phase": "Development", "duration": "4 months"},
            {"phase": "Testing", "duration": "1 month"},
            {"phase": "Deployment", "duration": "2 weeks"},
        ],
    }

    print(f"   ✓ Project APPROVED: {final_approval['project_id']}")
    print(f"   ✓ Approved by: {final_approval['approved_by']}")
    print(f"   ✓ Start date: {final_approval['start_date']}")
    print("   Milestones:")
    for milestone in final_approval["milestones"]:
        print(f"      • {milestone['phase']}: {milestone['duration']}")

    await event_bus.publish(
        Event(
            event_type="workflow.step.complete",
            source="IV",
            data={
                "workflow_id": workflow_id,
                "step": "final_approval",
                "result": "approved",
            },
        )
    )

    await asyncio.sleep(0.5)

    # ===== Workflow Summary =====
    print("\n" + "=" * 80)
    print("✅ WORKFLOW COMPLETE")
    print("=" * 80)

    workflow_state = orchestrator.workflows.get(workflow_id)
    if workflow_state:
        print(f"\nWorkflow ID: {workflow_state['id']}")
        print(f"Status: {workflow_state['status']}")
        print(f"Started: {workflow_state['started_at']}")
        print(f"\nSteps Completed ({len(workflow_state['steps_completed'])}):")
        for i, step in enumerate(workflow_state["steps_completed"], 1):
            print(f"   {i}. {step['step']}: {step['result']}")

    # Governance metrics
    print("\n📊 Governance Metrics:")
    dashboard = governance.get_governance_dashboard()
    print(f"   Active Domains: {dashboard['ecosystem']['active_domains']}")
    print(f"   Active Integrations: {dashboard['ecosystem']['active_integrations']}")
    print(
        f"   Ecosystem Compliance: {dashboard['compliance']['ecosystem_percentage']:.1f}%"
    )

    print("\n💡 Key Insights:")
    print(f"   • {len(domains)} domains collaborated seamlessly")
    print(f"   • {len(integration_pairs)} cross-domain integrations used")
    print(f"   • {len(workflow_state['steps_completed'])} workflow steps executed")
    print("   • Full governance compliance maintained")
    print("   • Complete audit trail captured")

    print("\n🎯 Business Value:")
    print(f"   • Project: {project['name']}")
    print(f"   • Investment: ${project['estimated_budget']:,}")
    print(f"   • Timeline: {project['duration_months']} months")
    print(f"   • Team: {project['team_size']} engineers")
    print("   • Status: APPROVED & FUNDED")

    print("\n" + "=" * 80)


if __name__ == "__main__":
    asyncio.run(innovation_project_workflow())
