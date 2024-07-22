from ragflow.rag.app import paper, laws, naive, one, table, book, manual
import logging
import traceback
from share.constants import Constants as ShareConstants
debug_logger = logging.getLogger(ShareConstants.CHUNK_EXTRACT_LOGGER)

class RagflowWrapper():
    def __init__(self):
        self.request_payload = dict()
        self.parser_factory = {
            "paper": RagflowPaperStrategy,
            "general": RagflowNaiveStrategy,
            "law": RagflowLawStrategy,
            "book": RagflowBookStrategy,
            "manual": RagflowManualStrategy,
            "one": RagflowOneStrategy,
            "excel": RagflowExcelStrategy
        }

    def get_extraction_strategy(self, strategy_name):
        try:
            if strategy_name in self.parser_factory:
                return self.parser_factory[strategy_name]()
            else:
                raise ValueError(f"{strategy_name} strategy does not exist")

        except Exception as e:
            debug_logger.error(traceback.format_exc())
            raise ValueError(f"Exception: {strategy_name} strategy does not exist")

    def callback(self, prog=None, msg=""):
        try:
            debug_logger.info("Layout Extraction Status:- {}".format(msg))
        except Exception as e:
            debug_logger.error("Error in logging ragflow logs")
            debug_logger.error(traceback.format_exc())


class RagflowPaperStrategy(RagflowWrapper):
    def __init__(self):
        super().__init__()


    def extract_chunks(self, **request_payload):

        """
        Convert the given file content into chunks based on ragflow paper stratergy.
        Only pdf is supported.

        Args:
            document (dict): Documents for the given docIDs
            request_payload (dict): Payload from rabbitMq message broker

        Raises:
            ValueError:Executed when file type not supported (pdf supported).

        Returns:
            list of dict: Returns the extracted chunk from ragflow paper stratergy.
        """
        try:
            # self.document=document
            self.request_payload = request_payload
            filename = request_payload.get('local_file_path', '')
            extraction_config = request_payload.get('extraction_model', {}).get('config', {})
            ranges = extraction_config.get("pageRange", [[0, 100000]])
            request_payload['sys_file_type'] = request_payload.get("file_type", "")
            request_payload['extract_table_html'] = extraction_config.get('extractTableHTML', True)
            raw_chunks = list()
            for range in ranges:
                from_page = range[0]
                to_page = range[1]
                raw_chunks.extend(paper.chunk(filename=filename, fromPage=from_page, toPage=to_page, callback=self.callback,
                                           **request_payload))
            return raw_chunks
        except Exception as e:
            debug_logger.error("Ragflow Paper Strategy Failed to execute")
            debug_logger.error(traceback.format_exc())
            return []


class RagflowLawStrategy(RagflowWrapper):
    def __init__(self):
        super().__init__()

    def extract_chunks(self, **request_payload):
        """
        Convert the given file content into chunks based on ragflow law stratergy.
        Supported file formats are docx, pdf, txt

        Args:
            document (dict): Documents for the given docIDs
            request_payload (dict): Payload from rabbitMq message broker

        Raises:
            ValueError:Executed when file type not supported.

        Returns:
            list of dict: Returns the extracted chunk from ragflow law stratergy.
        """
        try:
            # self.document=document
            self.request_payload = request_payload
            filename = request_payload.get('local_file_path', '')
            extraction_config = request_payload.get('extraction_model', {}).get('config', {})
            ranges = extraction_config.get("pageRange", [[0, 100000]])
            request_payload['sys_file_type'] = request_payload.get("file_type", "")
            request_payload['extract_table_html'] = extraction_config.get('extractTableHTML', True)
            raw_chunks = list()
            for range in ranges:
                from_page = range[0]
                to_page = range[1]
                raw_chunks.extend(
                    laws.chunk(filename=filename, fromPage=from_page, toPage=to_page, callback=self.callback,
                                **request_payload))
            return raw_chunks

        except Exception as e:
            debug_logger.error("Ragflow Laws Strategy Failed to execute")
            debug_logger.error(traceback.format_exc())
            return []


class RagflowNaiveStrategy(RagflowWrapper):
    def __init__(self):
        super().__init__()

    def extract_chunks(self, **request_payload):
        """
        Convert the given file content into chunks based on ragflow naive stratergy.
        Supported file formats are docx, pdf, excel, txt.

        Args:
            document (dict): Documents for the given docIDs
            request_payload (dict): Payload from rabbitMq message broker

        Raises:
            ValueError:Executed when file type not supported.

        Returns:
            list of dict: Returns the extracted chunk from ragflow naive stratergy.
        """
        try:
            self.request_payload = request_payload
            filename = request_payload.get('local_file_path', '')
            extraction_config = request_payload.get('extraction_model', {}).get('config', {})
            ranges = extraction_config.get("pageRange", [[0, 100000]])
            request_payload['extract_table_html'] = extraction_config.get('extractTableHTML', True)
            request_payload['chunk_size'] = extraction_config.get('chunkLength', 1000)
            request_payload['delimiter'] = extraction_config.get('textSplitter', 100)
            request_payload['sys_file_type'] = request_payload.get("file_type", "")
            raw_chunks = list()
            for range in ranges:
                from_page = range[0]
                to_page = range[1]
                raw_chunks.extend(
                    naive.chunk(filename=filename, fromPage=from_page, toPage=to_page, callback=self.callback,
                                **request_payload))
            return raw_chunks

        except Exception as e:
            debug_logger.error("Ragflow Naive Strategy Failed to execute")
            debug_logger.error(traceback.format_exc())
            return []


class RagflowOneStrategy(RagflowWrapper):
    def __init__(self):
        super().__init__()

    def extract_chunks(self, **request_payload):
        """
        Convert the given file content into chunks based on ragflow one stratergy.
        Supported file formats are docx, pdf, excel, txt.

        Args:
            document (dict): Documents for the given docIDs
            request_payload (dict): Payload from rabbitMq message broker

        Raises:
            ValueError:Executed when file type not supported.

        Returns:
            list of dict: Returns the extracted chunk from ragflow one stratergy.
        """
        try:
            self.request_payload = request_payload
            filename = request_payload.get('local_file_path', '')
            extraction_config = request_payload.get('extraction_model', {}).get('config', {})
            ranges = extraction_config.get("pageRange", [[0, 100000]])
            request_payload['extract_table_html'] = extraction_config.get('extractTableHTML', True)
            request_payload['chunk_size'] = extraction_config.get('chunkLength', 1000)
            request_payload['delimiter'] = extraction_config.get('textSplitter', 100)
            request_payload['sys_file_type'] = request_payload.get("file_type", "")
            raw_chunks = list()
            for range in ranges:
                from_page = range[0]
                to_page = range[1]
                raw_chunks.extend(
                    one.chunk(filename=filename, fromPage=from_page, toPage=to_page, callback=self.callback,
                                **request_payload))
            return raw_chunks

        except Exception as e:
            debug_logger.error("Ragflow One Strategy Failed to execute")
            debug_logger.error(traceback.format_exc())
            return []


class RagflowExcelStrategy(RagflowWrapper):
    def __init__(self):
        super().__init__()

    def extract_chunks(self, **request_payload):
        """
        Convert the given file content into chunks based on ragflow excel stratergy.
        Excel and csv(txt) format files are supported.
        For csv or txt file, the delimiter between columns is TAB.
        The first line must be column headers.

        Args:
            document (dict): Documents for the given docIDs
            request_payload (dict): Payload from rabbitMq message broker

        Raises:
            ValueError:Executed when file type not supported.

        Returns:
            list of dict: Returns the extracted chunk from ragflow excel stratergy.
        """
        try:
            self.request_payload = request_payload
            filename = request_payload.get('local_file_path', '')
            extraction_config = request_payload.get('extraction_model', {}).get('config', {})
            ranges = extraction_config.get("rowRange", [[0, 100000]])
            request_payload['sys_file_type'] = request_payload.get("file_type", "")
            raw_chunks = list()
            for range in ranges:
                from_page = range[0]
                to_page = range[1]
                raw_chunks.extend(
                    table.chunk(filename=filename, fromPage=from_page, toPage=to_page, callback=self.callback,
                                **request_payload))
            return raw_chunks

        except Exception as e:
            debug_logger.error("Ragflow Excel Strategy Failed to execute")
            debug_logger.error(traceback.format_exc())
            return []


class RagflowBookStrategy(RagflowWrapper):
    def __init__(self):
        super().__init__()

    def extract_chunks(self, **request_payload):
        """
        Convert the given file content into chunks based on ragflow book stratergy.
        Supported file formats are docx, pdf, txt.

        Args:
            document (dict): Documents for the given docIDs
            request_payload (dict): Payload from rabbitMq message broker

        Raises:
            ValueError:Executed when file type not supported.

        Returns:
            list of dict: Returns the extracted chunk from ragflow book stratergy.
        """
        try:
            self.request_payload = request_payload
            filename = request_payload.get('local_file_path', '')
            extraction_config = request_payload.get('extraction_model', {}).get('config', {})
            ranges = extraction_config.get("pageRange", [[0, 100000]])
            request_payload['extract_table_html'] = extraction_config.get('extractTableHTML', True)
            request_payload['chunk_size'] = extraction_config.get('chunkLength', 1000)
            request_payload['delimiter'] = extraction_config.get('textSplitter', 100)
            request_payload['sys_file_type'] = request_payload.get("file_type", "")
            raw_chunks = list()
            for range in ranges:
                from_page = range[0]
                to_page = range[1]
                raw_chunks.extend(
                    book.chunk(filename=filename, fromPage=from_page, toPage=to_page, callback=self.callback,
                                **request_payload))
            return raw_chunks

        except Exception as e:
            debug_logger.error("Ragflow Book Strategy Failed to execute")
            debug_logger.error(traceback.format_exc())
            return []


class RagflowManualStrategy(RagflowWrapper):
    def __init__(self):
        super().__init__()

    def extract_chunks(self, **request_payload):
        """
        Convert the given file content into chunks based on ragflow manual stratergy.
        Only pdf is supported.

        Args:
            document (dict): Documents for the given docIDs
            request_payload (dict): Payload from rabbitMq message broker

        Raises:
            ValueError:Executed when file type not supported.

        Returns:
            list of dict: Returns the extracted chunk from ragflow manual stratergy.
        """
        try:
            self.request_payload = request_payload
            filename = request_payload.get('local_file_path', '')
            extraction_config = request_payload.get('extraction_model', {}).get('config', {})
            ranges = extraction_config.get("pageRange", [[0, 100000]])
            request_payload['extract_table_html'] = extraction_config.get('extractTableHTML', True)
            request_payload['chunk_size'] = extraction_config.get('chunkLength', 1000)
            request_payload['delimiter'] = extraction_config.get('textSplitter', 100)
            request_payload['sys_file_type'] = request_payload.get("file_type", "")
            raw_chunks = list()
            for range in ranges:
                from_page = range[0]
                to_page = range[1]
                raw_chunks.extend(
                    manual.chunk(filename=filename, fromPage=from_page, toPage=to_page, callback=self.callback,
                                **request_payload))
            return raw_chunks

        except Exception as e:
            debug_logger.error("Ragflow Manual Strategy Failed to execute")
            debug_logger.error(traceback.format_exc())
            return []



