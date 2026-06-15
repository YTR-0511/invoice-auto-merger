"""报销完成后调用：删除【待报销的发票】和【发票附件】下的所有 PDF（保留文件夹结构）
以及 notebook 生成的合成 PDF【最终_全部图片化_发票带粘贴单.pdf】。

用法：
    python 清理.py
脚本会先列出要删的文件，输入 y 确认后才会真正删除。
"""
from pathlib import Path

INVOICE_ROOT = Path("待报销的发票")
ATTACHMENT_ROOT = Path("发票附件")
OUTPUT_PDF = Path("最终_全部图片化_发票带粘贴单.pdf")


def main():
    invoice_pdfs = sorted(INVOICE_ROOT.rglob("*.pdf")) if INVOICE_ROOT.is_dir() else []
    attachment_pdfs = sorted(ATTACHMENT_ROOT.rglob("*.pdf")) if ATTACHMENT_ROOT.is_dir() else []
    output_pdfs = [OUTPUT_PDF] if OUTPUT_PDF.exists() else []
    targets = invoice_pdfs + attachment_pdfs + output_pdfs

    if not targets:
        print("没有需要清理的文件。")
        return

    print(f"将删除以下 {len(targets)} 个文件：")
    for p in targets:
        print(f"  - {p}")

    answer = input("\n确认删除？(y/N): ").strip().lower()
    if answer != "y":
        print("已取消。")
        return

    deleted = 0
    for p in targets:
        try:
            p.unlink()
            deleted += 1
        except OSError as e:
            print(f"删除失败 {p}: {e}")

    print(f"\n清理完成，共删除 {deleted} 个文件。类目子文件夹与发票附件文件夹结构已保留。")


if __name__ == "__main__":
    main()
