"""
DHIS2 pipeline orchestration.

Coordinates extraction, transformation, validation,
and loading of DHIS2 records.
"""


from hip.audit.service import AuditService
from hip.extractors.base import BaseExtractor
from hip.loaders.base import BaseLoader
from hip.pipelines.base import BasePipeline
from hip.pipelines.config import PipelineConfig
from hip.pipelines.context import PipelineContext
from hip.pipelines.request import PipelineRequest
from hip.transformers.base import BaseTransformer
from hip.validators.base import BaseValidator


class DHIS2Pipeline(BasePipeline):
    """Pipeline for processing DHIS2 data."""

    pipeline_type = "dhis2"

    def __init__(
        self,
        extractor: BaseExtractor,
        transformer: BaseTransformer,
        validator: BaseValidator,
        loader: BaseLoader,
        audit: AuditService,
        config: PipelineConfig,
    ) -> None:
        super().__init__(
            extractor=extractor,
            transformer=transformer,
            validator=validator,
            loader=loader,
        )
        self.audit = audit
        self.config = config

    def run(
        self,
        request: PipelineRequest,
    ) -> int:
        """Extract, transform, validate, and load DHIS2 records."""

        batch_id = self.audit.start_batch(
            source_system="DHIS2",
            batch_name=self.config.batch_name,
            environment=self.config.environment,
            initiated_by=self.config.initiated_by,
        )

        context = PipelineContext(
            batch_id=batch_id,
            environment=self.config.environment,
            initiated_by=self.config.initiated_by,
        )
        
        raw_records = []

        try:
            response = self.extractor.extract(request)

            raw_records = response.get("dataValues", [])
            dataset_id = response.get("dataSet")
            
            valid_records = []
            failed_rows = 0

            for raw_record in raw_records:
                enriched_record = {
                    **raw_record,
                    "dataSet": dataset_id,
                }

                transformed_record = self.transformer.transform(
                    enriched_record,
                    context=context,
                )

                if self.validator.validate(transformed_record):
                    valid_records.append(transformed_record)
                else:
                    failed_rows += 1

            
            if not valid_records:
                self.audit.complete_batch(
                    batch_id=batch_id,
                    total_rows=len(raw_records),
                    successful_rows=0,
                    failed_rows=failed_rows,
                )
                return 0

            load_result = self.loader.load(valid_records)

            self.audit.complete_batch(
                batch_id=batch_id,
                total_rows=len(raw_records),
                successful_rows=(
                    load_result.inserted_rows
                    + load_result.duplicate_rows
                ),
                failed_rows=failed_rows,
            )

            return load_result.inserted_rows

        except Exception as exc:
            self.audit.fail_batch(
                batch_id=batch_id,
                total_rows=len(raw_records),
                successful_rows=0,
                failed_rows=len(raw_records),
                remarks=str(exc),
            )

            raise
