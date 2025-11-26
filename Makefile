run:
	@./tailwindcss -i ./static/css/input.css -o ./static/css/output.css
	@fastapi dev intellidoc.py

tailwind-install:
	@echo "Downloading TailwindCSS CLI..."
	@wget https://github.com/tailwindlabs/tailwindcss/releases/latest/download/tailwindcss-linux-x64 -O tailwindcss
	@chmod +x tailwindcss