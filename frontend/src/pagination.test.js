import { describe, expect, it } from "vitest";
import { paginateItems } from "./pagination";

describe("paginateItems", () => {
  it("returns the requested page and navigation metadata", () => {
    const result = paginateItems(["a", "b", "c", "d", "e"], 2, 2);
    expect(result.items).toEqual(["c", "d"]);
    expect(result.currentPage).toBe(2);
    expect(result.totalPages).toBe(3);
    expect(result.hasPrevious).toBe(true);
    expect(result.hasNext).toBe(true);
  });

  it("clamps invalid pages and handles an empty collection", () => {
    expect(paginateItems(["a"], 8, 2).currentPage).toBe(1);
    expect(paginateItems([], 0, 2)).toMatchObject({
      items: [],
      currentPage: 1,
      totalPages: 1,
      hasPrevious: false,
      hasNext: false,
    });
  });
});
