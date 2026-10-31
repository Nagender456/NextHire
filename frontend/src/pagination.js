export const DEFAULT_PAGE_SIZE = 10;

export function paginateItems(items, page, pageSize = DEFAULT_PAGE_SIZE) {
  const safePageSize = Math.max(1, Number(pageSize) || DEFAULT_PAGE_SIZE);
  const totalPages = Math.max(1, Math.ceil(items.length / safePageSize));
  const currentPage = Math.min(Math.max(1, Number(page) || 1), totalPages);
  const start = (currentPage - 1) * safePageSize;
  return {
    items: items.slice(start, start + safePageSize),
    currentPage,
    totalPages,
    hasPrevious: currentPage > 1,
    hasNext: currentPage < totalPages,
  };
}
