#!/usr/bin/env python3
"""
Create embeddings-ready chunks from documentation
Splits large documents into semantic chunks suitable for vector embeddings
"""

import json
import re
from pathlib import Path
from typing import List, Dict

def split_markdown_by_headings(content: str, max_chunk_size: int = 1000) -> List[Dict]:
    """Split markdown by headings, keeping chunks under max_chunk_size"""
    chunks = []
    lines = content.splitlines()
    current_chunk = []
    current_heading = ""
    current_path = []

    for line in lines:
        # Detect heading
        heading_match = re.match(r'^(#{1,6})\s+(.+)$', line)

        if heading_match:
            # Save previous chunk if it exists
            if current_chunk:
                chunk_text = '\n'.join(current_chunk).strip()
                if chunk_text:
                    chunks.append({
                        'heading': current_heading,
                        'heading_path': ' > '.join(current_path),
                        'content': chunk_text,
                        'char_count': len(chunk_text)
                    })

            # Start new chunk
            level = len(heading_match.group(1))
            heading_text = heading_match.group(2)

            # Update heading path
            current_path = current_path[:level-1] + [heading_text]
            current_heading = heading_text
            current_chunk = [line]
        else:
            current_chunk.append(line)

            # If chunk is getting too large, split it
            chunk_text = '\n'.join(current_chunk)
            if len(chunk_text) > max_chunk_size:
                chunks.append({
                    'heading': current_heading,
                    'heading_path': ' > '.join(current_path),
                    'content': chunk_text.strip(),
                    'char_count': len(chunk_text)
                })
                current_chunk = []

    # Save final chunk
    if current_chunk:
        chunk_text = '\n'.join(current_chunk).strip()
        if chunk_text:
            chunks.append({
                'heading': current_heading,
                'heading_path': ' > '.join(current_path),
                'content': chunk_text,
                'char_count': len(chunk_text)
            })

    return chunks

def process_documentation(repo_path: str = "/opt/documentation", output_file: str = "embeddings_chunks.json"):
    """Process all documentation into embedding-ready chunks"""
    repo = Path(repo_path)
    docs_path = repo / "docs"
    all_chunks = []

    for md_file in docs_path.rglob("*.md"):
        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()

            chunks = split_markdown_by_headings(content, max_chunk_size=1000)

            for i, chunk in enumerate(chunks):
                all_chunks.append({
                    'id': f"{md_file.stem}-{i}",
                    'source_file': str(md_file.relative_to(repo)),
                    'chunk_index': i,
                    'heading': chunk['heading'],
                    'heading_path': chunk['heading_path'],
                    'content': chunk['content'],
                    'char_count': chunk['char_count'],
                    'token_estimate': chunk['char_count'] // 4  # Rough estimate
                })

            print(f"✅ Processed {md_file.name}: {len(chunks)} chunks")

        except Exception as e:
            print(f"❌ Error processing {md_file}: {e}")

    # Save to JSON
    with open(output_file, 'w') as f:
        json.dump(all_chunks, f, indent=2)

    print(f"\n✅ Created {len(all_chunks)} embedding chunks")
    print(f"📁 Saved to: {output_file}")
    print(f"📊 Total estimated tokens: {sum(c['token_estimate'] for c in all_chunks):,}")

if __name__ == "__main__":
    process_documentation()
