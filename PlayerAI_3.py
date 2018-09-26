import random
from BaseAI_3 import BaseAI
import time
from ComputerAI_3 import ComputerAI

# Time Limit Before Losing
timeLimit = .18
LARGENUM = 100000000
directions = [0,1,2,3]

class PlayerAI(BaseAI):
	def __init__(self):
		self.idx2row = []
		self.indextorow()
		self.monotonicityvalues()


	def monotonicityvalues(self):
		self.monotonetable = {}
		for possrow in self.idx2row:
			left = right = monotone = monotoneright = 0
			for y in range(3):
				if possrow[y]!=0 and possrow[y] >= possrow[y+1]:
					left += 4*(monotone ** 2)
				else:
					left -= abs(possrow[y]- possrow[y+1]) * 1.5
					monotone = 0
				if possrow[y] <= possrow[y+1] and possrow[y+1]:
					monotoneright += 1
					right += 4*(monotoneright ** 2)
				else:
					right -= abs(possrow[y]- possrow[y+1]) * 1.5
					monotoneright = 0
			self.monotonetable[possrow] = left, right

	def heuristic_monotone(self, grid):
		left = right = up = down = leftright = updown = 0
		a = grid.map
		grid2 = [(a[0][3], a[1][3], a[2][3], a[3][3]),(a[0][2], a[1][2], a[2][2], a[3][2]),(a[0][1], a[1][1], a[2][1], a[3][1]), (a[0][0], a[1][0], a[2][0], a[3][0])]
		for x in range(4):
			leftiter, rightiter = self.monotonetable[tuple(grid.map[x])]
			left += leftiter
			right += rightiter
			Upiter, Downiter = self.monotonetable[tuple(grid2[x])]
			up += Upiter
			down += Downiter
		return max(up, down) + max(left, right)

	# we use this to evaluate terminal nodes or any nodes
	def heuristic(self, grid):
		nonempty = 16-len(grid.getAvailableCells())
		return self.heuristic_monotone(grid)+self.heuristic_smoothness(grid)-(nonempty**2)

	# eval for smoothness
	def heuristic_smoothness(self, grid):
		v1, v2, v3, v4 = grid.map[0]
		v5, v6, v7, v8 = grid.map[1]
		v9, v10, v11, v12 = grid.map[2]
		v13, v14, v15, v16 = grid.map[3]
		for var in [v1, v2, v3, v4, v5, v6, v7, v8, v9, v10, v11, v12, v13, v14, v15, v16]:
			if var == 0:
				var = 2
		smoothness = - min(abs(v1-v2), abs(v1-v5)) - min(abs(v2-v1), abs(v2-v6), abs(v2-v3)) - min(abs(v3-v2), abs(v3-v7), abs(v3-v4)) - min(abs(v4-v3), abs(v4-v8))
		smoothness = smoothness - min(abs(v5-v1), abs(v5-v6), abs(v5-v9)) - min(abs(v6-v2), abs(v6-v5), abs(v6-v7), abs(v6-v10)) - min(abs(v7-v3), abs(v7-v6), abs(v7-v8), abs(v7-v11)) - min(abs(v8-v4), abs(v8-v7), abs(v8-v12))
		smoothness = smoothness - min(abs(v9-v5), abs(v9-v10), abs(v9-v13))- min(abs(v10-v6), abs(v10-v9), abs(v10-v11), abs(v10-v14)) - min(abs(v11-v7), abs(v11-v10), abs(v11-v12), abs(v11-v15))- min(abs(v12-v8), abs(v12-v11), abs(v12-v16))
		smoothness = smoothness - min(abs(v13-v14), abs(v13-v9)) - min(abs(v14-v13), abs(v14-v10), abs(v14-v15)) - min(abs(v15-v14), abs(v15-v11), abs(v15-v16)) - min(abs(v16-v15), abs(v16-v12))
		return smoothness

	# check if over time
	def overtime(self, currTime):
		if currTime - self.prevTime > timeLimit:
			self.over = True
			return True
		else:
			return False

	#build out all possible row values
	def indextorow(self):
		posstiles = [2**n for n in range(1, 16)]
		posstiles.append(0)
		for p1 in posstiles:
			for p2 in posstiles:
				for p3 in posstiles:
					for p4 in posstiles:
						possrow = p1, p2, p3, p4
						self.idx2row.append(possrow)

	#includes both the minimize and expectation steps; and alpha beta pruning
	def expectiminimax(self, grid, level, probofnode, alpha, beta):
		if level == 0 or self.overtime(time.clock()):
			return self.heuristic(grid)
		numEmpty = len(grid.getAvailableCells())
		worst_utility = LARGENUM
		for i in range(4):
			for j in range(4):
				if grid.map[i][j] !=0: #focus on empty cells
					continue
				newgridrow = list(grid.map[i]) #the row in the grid
				utility = 0
				totalprobability = 0
				for probability, tilevalue in ((0.1, 4), (0.9, 2)):
					pp = probability*probofnode
					if 0.9 * pp < 0.1 and numEmpty > 4 :
						continue
					newgridrow[j] = tilevalue
					grid.map[i] = newgridrow
					utility += probability *self.maximize(grid, level, pp, alpha, beta)
					totalprobability+=probability
				newgridrow[j] = 0 #changed it back!
				grid.map[i] = newgridrow #changed it back!
				if totalprobability == 0:
					utility = self.heuristic(grid)
				else:
					utility /=totalprobability
				if utility < worst_utility:
					worst_utility = utility
				if worst_utility <= alpha:
					break
				if worst_utility < beta:
					beta = worst_utility
		return worst_utility

	#maximization step
	def maximize(self, grid, level, probofnode, alpha, beta):
		maxUtility = -LARGENUM
		for d in directions:
			g2 = grid.clone()
			successful = g2.move(d)
			if not successful:
				continue
			utility = self.expectiminimax(g2, level -1, probofnode, alpha, beta)
			if utility> maxUtility:
				maxUtility = utility
			if maxUtility >= beta:
				break
			if maxUtility > alpha:
				alpha = maxUtility
		return maxUtility


	# most importantly, give the next move
	def getMove(self, grid):
		self.prevTime = time.clock()
		maxUtility = -LARGENUM
		decision = random.choice(directions)
		alpha = -LARGENUM
		beta = LARGENUM

		for d in directions:
			g2 = grid.clone()
			successful = g2.move(d)
			if not successful:
				continue
			utility = self.expectiminimax(g2, 2 - 1, 1.0, alpha, beta)
			if utility > maxUtility:
				maxUtility = utility
				decision = d
			if maxUtility >= beta:
				break
			if maxUtility > alpha:
				alpha = maxUtility


		return decision