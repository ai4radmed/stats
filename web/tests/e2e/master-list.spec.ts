import { test, expect } from '@playwright/test';

test.describe('의약품 마스터 리스트 페이지', () => {
  test('페이지가 정상적으로 로드되고 타이틀이 표시된다', async ({ page }) => {
    // 로컬 개발 서버 주소 (Astro dev)
    await page.goto('/master-list');

    // 타이틀 확인
    const title = page.locator('h1');
    await expect(title).toHaveText('방사성의약품 마스터 리스트');

    // 상태 카드 확인
    const statusCards = page.locator('.status-card');
    await expect(statusCards).toHaveCount(3);
  });

  test('의약품 목록 테이블이 존재한다', async ({ page }) => {
    await page.goto('/master-list');

    // 테이블 헤더 확인
    const headers = page.locator('th');
    await expect(headers).toHaveCount(12);
    await expect(headers.nth(0)).toHaveText('No.');
    await expect(headers.last()).toHaveText('EDI 코드');

    // 트래픽 정보 확인
    const trafficInfo = page.locator('text=/트래픽 사용량/');
    await expect(trafficInfo).toBeVisible();
    
    // 데이터 로드 확인 (적어도 하나 이상의 데이터 행이 있는지)
    // 실제 DB 데이터가 있으므로 행이 보여야 함
    const rows = page.locator('tbody tr');
    await expect(rows.count()).resolves.toBeGreaterThan(0);
  });

  test('메인 페이지로 돌아가는 링크가 작동한다', async ({ page }) => {
    await page.goto('/master-list');
    
    const backLink = page.locator('a:has-text("메인으로 돌아가기")');
    await expect(backLink).toBeVisible();
    
    await backLink.click();
    await expect(page).toHaveURL('/');
  });
});
