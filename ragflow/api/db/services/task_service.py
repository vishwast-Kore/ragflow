#
#  Copyright 2024 The InfiniFlow Authors. All Rights Reserved.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#
import random

from peewee import Expression, JOIN
from api.db.db_models import DB, File2Document, File
from api.db import StatusEnum, FileType, TaskStatus
from api.db.db_models import Task, Document, Knowledgebase, Tenant
from api.db.services.common_service import CommonService
from api.db.services.document_service import DocumentService
from api.utils import current_timestamp


class TaskService(CommonService):
    model = Task

    @classmethod
    @DB.connection_context()
    def get_tasks(cls, tm, mod=0, comm=1, items_per_page=1, takeit=True):
        fields = [
            cls.model.id,
            cls.model.doc_id,
            cls.model.from_page,
            cls.model.to_page,
            Document.kb_id,
            Document.parser_id,
            Document.parser_config,
            Document.name,
            Document.type,
            Document.location,
            Document.size,
            Knowledgebase.tenant_id,
            Knowledgebase.language,
            Knowledgebase.embd_id,
            Tenant.img2txt_id,
            Tenant.asr_id,
            cls.model.update_time]
        with DB.lock("get_task", -1):
            docs = cls.model.select(*fields) \
                .join(Document, on=(cls.model.doc_id == Document.id)) \
                .join(Knowledgebase, on=(Document.kb_id == Knowledgebase.id)) \
                .join(Tenant, on=(Knowledgebase.tenant_id == Tenant.id))\
                .where(
                    Document.status == StatusEnum.VALID.value,
                    Document.run == TaskStatus.RUNNING.value,
                    ~(Document.type == FileType.VIRTUAL.value),
                    cls.model.progress == 0,
                    #cls.model.update_time >= tm,
                    #(Expression(cls.model.create_time, "%%", comm) == mod)
                )\
                .order_by(cls.model.update_time.asc())\
                .paginate(0, items_per_page)
            docs = list(docs.dicts())
            if not docs: return []
            if not takeit: return docs

            cls.model.update(progress_msg=cls.model.progress_msg + "\n" + "Task has been received.", progress=random.random()/10.).where(
                cls.model.id == docs[0]["id"]).execute()
            return docs

    @classmethod
    @DB.connection_context()
    def get_ongoing_doc_name(cls):
        with DB.lock("get_task", -1):
            docs = cls.model.select(*[Document.id, Document.kb_id, Document.location, File.parent_id]) \
                .join(Document, on=(cls.model.doc_id == Document.id)) \
                .join(File2Document, on=(File2Document.document_id == Document.id), join_type=JOIN.LEFT_OUTER) \
                .join(File, on=(File2Document.file_id == File.id), join_type=JOIN.LEFT_OUTER) \
                .where(
                    Document.status == StatusEnum.VALID.value,
                    Document.run == TaskStatus.RUNNING.value,
                    ~(Document.type == FileType.VIRTUAL.value),
                    cls.model.progress < 1,
                    cls.model.create_time >= current_timestamp() - 1000 * 600
                )
            docs = list(docs.dicts())
            if not docs: return []

            return list(set([(d["parent_id"] if d["parent_id"] else d["kb_id"], d["location"]) for d in docs]))

    @classmethod
    @DB.connection_context()
    def do_cancel(cls, id):
        try:
            task = cls.model.get_by_id(id)
            _, doc = DocumentService.get_by_id(task.doc_id)
            return doc.run == TaskStatus.CANCEL.value or doc.progress < 0
        except Exception as e:
            pass
        return True

    @classmethod
    @DB.connection_context()
    def update_progress(cls, id, info):
        with DB.lock("update_progress", -1):
            if info["progress_msg"]:
                cls.model.update(progress_msg=cls.model.progress_msg + "\n" + info["progress_msg"]).where(
                    cls.model.id == id).execute()
            if "progress" in info:
                cls.model.update(progress=info["progress"]).where(
                    cls.model.id == id).execute()
