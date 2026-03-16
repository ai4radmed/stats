# ai4radmed-stats 통합 관리 Makefile

.PHONY: sync dev run-stats deploy clean check

# 1. 환경 동기화 (Git Pull + Triple-Stack Update)
sync:
	@echo ">> 1. Pulling latest code from GitHub..."
	git pull
	@echo ">> 2. Syncing Python dependencies (uv)..."
	cd scripts && uv sync
	@echo ">> 3. Syncing R dependencies (renv)..."
	cd analysis && Rscript -e "renv::restore()"
	@echo ">> 4. Syncing Frontend dependencies (Astro)..."
	cd web && npm install --legacy-peer-deps
	@echo "[SUCCESS] Project sync and update complete."

# 1-1. 실적 데이터 동기화 (Performance Data Only)
sync-perf:
	@echo ">> Syncing Product Performance Data (MFDS)..."
	cd scripts && uv run sync_performance.py
	@echo "[SUCCESS] Performance data synced to Supabase."

# 1-2. 임상시험 데이터 동기화 (Clinical Trial Data Only)
sync-clinical:
	@echo ">> Syncing Clinical Trial Data (MFDS)..."
	cd scripts && uv run sync_clinical_trials.py
	@echo "[SUCCESS] Clinical trial data synced to Supabase."

# 2. 분석 엔진 실행 (Data Pipeline)
run-stats:
	@echo ">> Running Statistical Pipeline (Python -> R)..."
	cd scripts && uv run main.py
	@echo "[SUCCESS] Statistics updated in web/public/data/"

# 3. 개발 서버 실행
dev:
	@echo ">> Starting Astro Development Server..."
	cd web && npm run dev

# 4. 품질 검증
check:
	@echo ">> Running Lint and Tests (Frontend)..."
	cd web && npm run test
	@echo ">> Running Style Check (Python)..."
	cd scripts && uv sync && uv run ruff check .

# 5. 청소
clean:
	rm -rf web/node_modules scripts/.venv analysis/renv/library
