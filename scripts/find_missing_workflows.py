"""
Find missing workflow files by comparing inventory to actual files.
"""
import os
from pathlib import Path

# Complete inventory from WORKFLOW_INVENTORY.md (121 workflows)
INVENTORY = {
    # Development (30)
    "development": [
        "technical_debt_identification.md",  # dev-001
        "test_writing.md",  # dev-002
        "third_party_api_integration.md",  # dev-003
        "type_annotation_addition.md",  # dev-004
        "ai_assisted_session.md",  # dev-005
        "developer_onboarding.md",  # dev-006
        "pair_programming_with_ai.md",  # dev-007
        "technical_debt_mgmt.md",  # dev-008
        "dependency_update_strategy.md",  # dev-009
        "dependency_upgrade.md",  # dev-010
        "log_analysis.md",  # dev-011
        "maint-011_cross_repo_changes.md",  # dev-012
        "refactoring_strategy.md",  # dev-013
        "module_creation_headers.md",  # dev-014
        "application_settings.md",  # dev-015
        "pydantic_settings.md",  # dev-016
        "if_project_has_formatter.md",  # dev-017
        "system_logs_config.md",  # dev-018
        "run_tests_coverage.md",  # dev-019
        "install_vercel_cli.md",  # dev-020
        "add_secrets_github_cli.md",  # dev-021
        "environment_initialization.md",  # dev-022
        "new_repo_scaffolding.md",  # dev-023
        "pre_commit_hooks.md",  # dev-024
        "ci_cd_workflow.md",  # dev-025
        "breaking_api_changes.md",  # dev-026
        "fastapi-endpoint-workflow.md",  # dev-027
        "legacy_code_integration.md",  # dev-028
        "spike-research-workflow.md",  # dev-029
        "code_review_response.md",  # dev-030
    ],
    # DevOps (15)
    "devops": [
        "application_monitoring_setup.md",  # dvo-001
        "auto_scaling_configuration.md",  # dvo-002
        "backup_disaster_recovery.md",  # dvo-003
        "cicd_pipeline_setup.md",  # dvo-004
        "cloud_provider_setup.md",  # dvo-005
        "docker_compose_multi_service.md",  # dvo-006
        "docker_container_creation.md",  # dvo-007
        "incident_response_workflow.md",  # dvo-008
        "infrastructure_as_code_terraform.md",  # dvo-009
        "kubernetes_deployment.md",  # dvo-010
        "log_aggregation_elk.md",  # dvo-011
        "performance_tuning.md",  # dvo-012
        "emergency_hotfix.md",  # dvo-013
        "incident_response.md",  # dvo-014
        "rollback_procedure.md",  # dvo-015
    ],
    # Frontend Development (11)
    "frontend-development": [
        "accessibility_workflow.md",  # fro-001
        "api_integration_patterns.md",  # fro-002
        "build_deployment.md",  # fro-003
        "component_testing_strategy.md",  # fro-004
        "e2e_testing_workflow.md",  # fro-005
        "form_handling_validation.md",  # fro-006
        "performance_optimization.md",  # fro-007
        "react_component_creation.md",  # fro-008
        "responsive_design_implementation.md",  # fro-009
        "state_management_setup.md",  # fro-010
        "frontend_build_deployment.md",  # fro-011
    ],
    # Machine Learning (10)
    "machine-learning": [
        "ab_testing_models.md",  # mac-001
        "automl_hyperparameter_optimization.md",  # mac-002
        "data_preprocessing_pipelines.md",  # mac-003
        "deep_learning_pytorch_tensorflow.md",  # mac-004
        "feature_engineering_selection.md",  # mac-005
        "mlops_pipeline_setup.md",  # mac-006
        "model_deployment_strategies.md",  # mac-007
        "model_monitoring_observability.md",  # mac-008
        "model_training_evaluation.md",  # mac-009
        "ml_experiment_setup.md",  # mac-010
    ],
    # Data Engineering (12)
    "data-engineering": [
        "big_data_processing_spark.md",  # dat-001
        "data_catalog_governance.md",  # dat-002
        "data_lake_architecture.md",  # dat-003
        "data_pipeline_architecture.md",  # dat-004
        "data_quality_validation.md",  # dat-005
        "data_transformation_dbt.md",  # dat-006
        "data_warehousing_modeling.md",  # dat-007
        "etl_pipeline_design.md",  # dat-008
        "pipeline_orchestration_airflow.md",  # dat-009
        "stream_processing_kafka.md",  # dat-010
        "database-migration-workflow.md",  # dat-011
        "ml_experiment_setup.md",  # dat-012
    ],
    # Architecture (9)
    "architecture": [
        "api_design_best_practices.md",  # arc-001
        "caching_strategies.md",  # arc-002
        "caching_strategy_implementation.md",  # arc-003
        "distributed_systems_patterns.md",  # arc-004
        "event_driven_architecture.md",  # arc-005
        "microservices_patterns.md",  # arc-006
        "scalability_patterns.md",  # arc-007
        "system_architecture_design.md",  # arc-008
        "architecture_decision_records.md",  # arc-009
    ],
    # Quality Assurance (10)
    "quality-assurance": [
        "code_review_checklist.md",  # qua-001
        "complexity_reduction.md",  # qua-002
        "coverage_gap_analysis.md",  # qua-003
        "deviation_protocol.md",  # qua-004
        "graduation_lite_to_strict.md",  # qua-005
        "mypy_type_fixing.md",  # qua-006
        "pr_creation_review.md",  # qua-007
        "quality_gate_execution.md",  # qua-008
        "ruff_error_resolution.md",  # qua-009
        "test_failure_investigation.md",  # qua-010
    ],
    # Security (6)
    "security": [
        "code_buddy_secret_rules.md",  # sec-001
        "git_history_cleanup_solo.md",  # sec-002
        "secret_incident_solo.md",  # sec-003
        "secret_management_solo.md",  # sec-004
        "anthropic_key_rotation.md",  # sec-005
        "openai_key_rotation.md",  # sec-006
    ],
    # Version Control (4)
    "version-control": [
        "branch_strategy.md",  # ver-001
        "commit_message_correction.md",  # ver-002
        "merge_conflict_resolution.md",  # ver-003
        "version_release_tagging.md",  # ver-004
    ],
    # Testing (5)
    "testing": [
        "performance_regression_investigation.md",  # tes-001
        "property_based_testing.md",  # tes-002
        "test-002_mocking_strategy.md",  # tes-003
        "test_data_generation.md",  # tes-004
        "test_writing.md",  # tes-005
    ],
    # Configuration Management (4)
    "configuration-management": [
        "application_settings.md",  # cfg-001
        "pydantic_settings_config.md",  # cfg-002
        "project_formatter_setup.md",  # cfg-003
        "system_logs_config.md",  # cfg-004
    ],
    # Project Management (4)
    "project-management": [
        "knowledge_transfer.md",  # prj-001
        "progress_tracking.md",  # prj-002
        "startup_resume.md",  # prj-003
        "token_management_handoff.md",  # prj-004
    ],
    # Discovery (1)
    "discovery": [
        "spike_research_workflow.md",  # dis-001
    ],
}

# Get actual files
workflows_dir = Path(r"C:\Repos\code_buddy_mcp\workflows")
existing_files = {}

for category in INVENTORY.keys():
    category_dir = workflows_dir / category
    if category_dir.exists():
        files = [f.name for f in category_dir.glob("*.md") if f.name not in ["_INDEX.md", "README.md"]]
        existing_files[category] = set(files)
    else:
        existing_files[category] = set()

# Find missing
missing = {}
total_missing = 0

for category, expected_files in INVENTORY.items():
    expected_set = set(expected_files)
    actual_set = existing_files.get(category, set())
    missing_files = expected_set - actual_set
    
    if missing_files:
        missing[category] = sorted(missing_files)
        total_missing += len(missing_files)

# Report
print("="*80)
print(f"MISSING WORKFLOWS REPORT")
print("="*80)
print(f"\nTotal in Inventory: 121")
print(f"Total Existing: {121 - total_missing}")
print(f"Total Missing: {total_missing}\n")

for category, files in sorted(missing.items()):
    print(f"\n{category.upper()} ({len(files)} missing)")
    print("-" * 80)
    for f in files:
        print(f"  - {f}")

print("\n" + "="*80)
print("SUMMARY")
print("="*80)
print("\nMissing by Category:")
for category, files in sorted(missing.items(), key=lambda x: len(x[1]), reverse=True):
    print(f"  {category}: {len(files)}")
