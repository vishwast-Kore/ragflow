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
import copy
from tika import parser
import re
from io import BytesIO
import os
import sys
sys.path.insert(
    0,
    os.path.abspath(
        os.path.join(
            os.path.dirname(
                os.path.abspath(__file__)),
            '../../')))
from rag.nlp import bullets_category, is_english, tokenize, remove_contents_table, \
    hierarchical_merge, make_colon_as_title, naive_merge, random_choices, tokenize_table, add_positions, \
    tokenize_chunks, find_codec
from rag.nlp import rag_tokenizer
from deepdoc.parser import PdfParser, DocxParser, PlainParser, HtmlParser


class Pdf(PdfParser):
    def __call__(self, filename, binary=None, from_page=0,
                 to_page=100000, zoomin=3,extract_table_html=True, callback=None):
        callback(msg="OCR is running...")
        self.__images__(
            filename if not binary else binary,
            zoomin,
            from_page,
            to_page,
            callback)
        callback(msg="OCR finished")

        from timeit import default_timer as timer
        start = timer()
        self._layouts_rec(zoomin)
        callback(0.67, "Layout analysis finished")
        print("layouts:", timer() - start)
        self._table_transformer_job(zoomin)
        callback(0.68, "Table analysis finished")
        self._text_merge()
        tbls = self._extract_table_figure(True, zoomin, extract_table_html, True)
        self._naive_vertical_merge()
        self._filter_forpages()
        self._merge_with_same_bullet()
        callback(0.75, "Text merging finished.")

        callback(0.8, "Text extraction finished")

        return [(b["text"] + self._line_tag(b, zoomin), b.get("layoutno", ""))
                for b in self.boxes], tbls


def chunk(filename, binary=None, from_page=0, to_page=100000,
          lang="Chinese", callback=None, **kwargs):
    """
        Supported file formats are docx, pdf, txt.
        Since a book is long and not all the parts are useful, if it's a PDF,
        please setup the page ranges for every book in order eliminate negative effects and save elapsed computing time.
    """
    doc = {
        "docnm_kwd": filename,
        "title_tks": rag_tokenizer.tokenize(re.sub(r"\.[a-zA-Z]+$", "", filename)),
        "type": "text"
    }
    chunk_token_size = kwargs.get("chunk_size", 400)
    delimiter = kwargs.get("delimiter", "\n。；！？" )
    parser_config = kwargs.get(
        "parser_config", {
            "chunk_token_num": chunk_token_size, "delimiter": delimiter, "layout_recognize": True})
    doc["title_sm_tks"] = rag_tokenizer.fine_grained_tokenize(doc["title_tks"])
    pdf_parser = None
    sections, tbls = [], []
    if kwargs.get("sys_file_type") == "docx":
        callback(0.1, "Start to parse.")
        doc_parser = DocxParser()
        # TODO: table of contents need to be removed
        sections, tbls = doc_parser(
            binary if binary else filename, from_page=from_page, to_page=to_page)
        remove_contents_table(sections, eng=is_english(
            random_choices([t for t, _ in sections], k=200)))
        tbls = [((None,"table",lns), None) for lns in tbls]
        callback(0.8, "Finish parsing.")

    elif kwargs.get("sys_file_type") == "pdf":
        pdf_parser = Pdf() if kwargs.get(
            "parser_config", {}).get(
            "layout_recognize", True) else PlainParser()
        sections, tbls = pdf_parser(filename if not binary else binary,
                                    from_page=from_page, to_page=to_page, callback=callback,extract_table_html=kwargs.get('extract_table_html',True))

    # elif re.search(r"\.txt$", filename, re.IGNORECASE):
    #     callback(0.1, "Start to parse.")
    #     txt = ""
    #     if binary:
    #         encoding = find_codec(binary)
    #         txt = binary.decode(encoding, errors="ignore")
    #     else:
    #         with open(filename, "r") as f:
    #             while True:
    #                 l = f.readline()
    #                 if not l:
    #                     break
    #                 txt += l
    #     sections = txt.split("\n")
    #     sections = [(l, "") for l in sections if l]
    #     remove_contents_table(sections, eng=is_english(
    #         random_choices([t for t, _ in sections], k=200)))
    #     callback(0.8, "Finish parsing.")

    # elif re.search(r"\.(htm|html)$", filename, re.IGNORECASE):
    #     callback(0.1, "Start to parse.")
    #     sections = HtmlParser()(filename, binary)
    #     sections = [(l, "") for l in sections if l]
    #     remove_contents_table(sections, eng=is_english(
    #         random_choices([t for t, _ in sections], k=200)))
    #     callback(0.8, "Finish parsing.")

    # elif re.search(r"\.doc$", filename, re.IGNORECASE):
    #     callback(0.1, "Start to parse.")
    #     binary = BytesIO(binary)
    #     doc_parsed = parser.from_buffer(binary)
    #     sections = doc_parsed['content'].split('\n')
    #     sections = [(l, "") for l in sections if l]
    #     remove_contents_table(sections, eng=is_english(
    #         random_choices([t for t, _ in sections], k=200)))
    #     callback(0.8, "Finish parsing.")

    else:
        raise NotImplementedError(
            "file type not supported yet(doc, docx, pdf, txt supported)")

    make_colon_as_title(sections)
    bull = bullets_category(
        [t for t in random_choices([t for t, _ in sections], k=100)])
    if bull >= 0:
        chunks = ["\n".join(ck)
                  for ck in hierarchical_merge(bull, sections, 5)]
    else:
        sections = [s.split("@") for s, _ in sections]
        sections = [(pr[0], "@" + pr[1]) if len(pr) == 2 else (pr[0], '') for pr in sections ]
        chunks = naive_merge(
            sections, parser_config.get(
                "chunk_token_num", 256), parser_config.get(
                "delimer", "\n。；！？"))

    # is it English
    # is_english(random_choices([t for t, _ in sections], k=218))
    eng = lang.lower() == "english"
    print("table contents",tbls)
    res = tokenize_table(tbls, doc, eng)
    res.extend(tokenize_chunks(chunks, doc, eng, pdf_parser))

    return res


if __name__ == "__main__":
    import sys

    def dummy(prog=None, msg=""):
        pass
    # chunk(sys.argv[1], from_page=1, to_page=10, callback=dummy)
    kwargs={"sys_file_type":"pdf"}
    result=chunk("/home/Ragul.Sivakumar/Downloads/sampleillustration.docx", callback=dummy,**kwargs)
    with open('bookResult.txt', 'w') as file:
        # Write the string to the file
        file.write(str(result))
