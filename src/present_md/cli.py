"""CLI interface for present-md."""

import os
import sys
import click
from dotenv import load_dotenv

from present_md.pipeline import PresentationPipeline


@click.group()
@click.version_option(version="1.0.0", prog_name="present-md")
def main():
    """present-md: Convert Markdown to beautiful PPTX presentations."""
    load_dotenv()


@main.command()
@click.option(
    "--input", "-i",
    "input_path",
    required=True,
    type=click.Path(exists=True),
    help="Path to the input Markdown (.md) file.",
)
@click.option(
    "--template", "-t",
    "template_path",
    required=True,
    type=click.Path(exists=True),
    help="Path to the Slide Master template (.pptx) file.",
)
@click.option(
    "--output", "-o",
    "output_path",
    required=False,
    type=click.Path(),
    default=None,
    help="Path for the output .pptx file. Defaults to output/<input_name>.pptx.",
)
@click.option(
    "--min-slides",
    default=10,
    type=int,
    help="Minimum number of slides (default: 10).",
)
@click.option(
    "--max-slides",
    default=15,
    type=int,
    help="Maximum number of slides (default: 15).",
)
def convert(input_path, template_path, output_path, min_slides, max_slides):
    """Convert a Markdown file to a PPTX presentation."""
    # Validate API key
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key or api_key == "your-openai-api-key-here":
        click.echo("Error: OPENAI_API_KEY is not set. Please set it in .env or environment.", err=True)
        sys.exit(1)

    # Generate default output path if not provided
    if output_path is None:
        os.makedirs("output", exist_ok=True)
        base_name = os.path.splitext(os.path.basename(input_path))[0]
        output_path = os.path.join("output", f"{base_name}.pptx")

    click.echo(f"📄 Input:    {input_path}")
    click.echo(f"🎨 Template: {template_path}")
    click.echo(f"📦 Output:   {output_path}")
    click.echo(f"📊 Slides:   {min_slides}–{max_slides}")
    click.echo()

    try:
        pipeline = PresentationPipeline(
            api_key=api_key,
            model=os.environ.get("OPENAI_MODEL", "gpt-4o"),
            min_slides=min_slides,
            max_slides=max_slides,
        )
        pipeline.run(input_path, template_path, output_path)
        click.echo(f"\n✅ Presentation saved to: {output_path}")
    except Exception as e:
        import traceback
        traceback.print_exc()
        click.echo(f"\n❌ Error: {e}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
