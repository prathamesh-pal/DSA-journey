# 1. Two Sum
# Difficulty: Easy
# Topics: Array, Hash Table
# Link: https://leetcode.com/problems/two-sum/
#
# You are given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target.
#
# You may assume that each input would have exactly one solution, and you may not use the same element twice.
#
# You can return the answer in any order.
#
#
#
# Example 1:
#
# Input: nums = [2,7,11,15], target = 9
#
# Output: [0,1]
#
# Explanation:
#
# The sum of nums[0] and nums[1] is 2 + 7 = 9, which equals the target. Therefore, the indices [0, 1] are returned.
#
# Example 2:
#
# Input: nums = [3,2,4], target = 6
#
# Output: [1,2]
#
# Explanation:
#
# The sum of nums[1] and nums[2] is 2 + 4 = 6, which equals the target. Therefore, the indices [1, 2] are returned.
#
# Example 3:
#
# Input: nums = [3,3], target = 6
#
# Output: [0,1]
#
# Explanation:
#
# The sum of nums[0] and nums[1] is 3 + 3 = 6, which equals the target. Therefore, the indices [0, 1] are returned.
#
#
#
# Constraints:
#
#
# 2 <= nums.length <= 104
#
#
# -109 <= nums[i] <= 109
#
#
# -109 <= target <= 109
#
#
# Only one valid answer exists.
#
#
#
# Follow-up: Can you come up with an algorithm that is less than O(n2) time complexity?
#
# --- My notes ---
# Approach:
# Use a hash map to store previously visited numbers and their indices.
# Calculate complement = target - nums[i].
# If complement exists, return its index and current index.
# Otherwise, store nums[i] and its index.

# Time complexity: O(n)

# Space complexity: O(n)

# What I got wrong / to revisit:
# Understand the complement concept.
# Remember to check the dictionary before inserting the current number.
# This avoids using the same element twice.
from typing import List, Optional

class Solution:
    def twoSum(self, nums: list[int], target: int) -> list[int]:
        seen = {}

        for i in range(len(nums)):
            complement = target - nums[i]

            if complement in seen:
                return [seen[complement], i]

            seen[nums[i]] = i

solution = Solution()

print(solution.twoSum([2, 7, 11, 15], 9))
print(solution.twoSum([3, 2, 4], 6))
print(solution.twoSum([3, 3], 6))