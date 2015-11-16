from __future__ import division
from copy import deepcopy
import math

class Algorithm(object):
    """
    Base class for an algorithm
    """
    def __init__(self):
        """
        Override if needed.
        """
        pass

    def train(self, X, y):
        """
        Train the algorithm.  Must override.
        """
        pass

    def predict(self, Z):
        """
        Predict using input data.  Must override.
        """
        pass

class Matrix(object):
    """
    Represent a matrix and allow for basic matrix operations to be done.
    """
    def __init__(self, X):
        """
        X - a list of lists, ie [[1],[1]]
        """
        #Validate that the input is ok
        self.validate(X)
        self.X = X

    def validate(self, X):
        """
        Validate that a given list of lists is a proper matrix
        X - a list of lists
        """
        list_error = "X must be a list of lists corresponding to a matrix, with each sub-list being a row."
        #Input must be a list
        if not isinstance(X, list):
            raise Exception(list_error)
        #All list elements must also be lists
        for i in xrange(0,len(X)):
            if not isinstance(X[i], list):
                raise Exception(list_error)

        #All rows must have equal length
        first_row_len = len(X[0])
        for i in xrange(0,len(X)):
            if len(X[i])!=first_row_len:
                raise Exception("All rows in X must be the same length.")

    def invert(self):
        """
        Invert the matrix in place.
        """
        self.X = invert(self.X)
        return self

    @property
    def rows(self):
        """
        Number of rows in the matrix
        """
        return len(self.X)

    @property
    def cols(self):
        """
        Number of columns in the matrix
        """
        return len(self.X[0])

    def transpose(self):
        """
        Transpose the matrix in place.
        """
        trans = []
        for j in xrange(0,self.cols):
            row = []
            for i in xrange(0,self.rows):
                row.append(self.X[i][j])
            trans.append(row)
        self.X = trans
        return self

    def __getitem__(self, key):
        """
        Get a row of the matrix, ie m=Matrix([[1],[1]]); m[0]
        """
        return self.X[key]

    def __setitem__(self, key, value):
        """
        Set a row of the matrix, ie m=Matrix([[1],[1]]); m[0] = [2]
        """
        assert self.cols == len(value)
        self.X[key] = value

    def set_column(self, key, value):
        """
        Set a column to a specific value
        """
        assert self.rows == len(value)
        for i in xrange(0,self.rows):
            self.X[i][key] = value[i]

    def __delitem__(self, key):
        """
        Delete a row of the matrix
        """
        del self.X[key]

    def del_column(self, key):
        """
        Delete a specified column
        """
        for i in xrange(0,self.rows):
            del self.X[i][key]

    def __len__(self):
        """
        Get the length of the matrix
        """
        return self.rows

    def __rmul__(self, Z):
        """
        Right hand multiplication, ie other_matrix * matrix
        """
        #Only 2 Matrix objects can be multiplied
        assert(isinstance(Z, Matrix))

        #Number of columns in other matrix must match number of rows in this matrix
        assert Z.cols==self.rows

        product = []
        for i in xrange(0,Z.rows):
            row = []
            for j in xrange(0,self.cols):
                row.append(row_multiply(Z.X[i], [self.X[m][j] for m in xrange(0,self.rows)]))
            product.append(row)
        return Matrix(product)

    def __mul__(self, Z):
        """
        Left hand multiplication, ie matrix * other_matrix
        """
        assert(isinstance(Z, Matrix))

        assert Z.rows==self.cols

        product = []
        for i in xrange(0,self.rows):
            row = []
            for j in xrange(0,Z.cols):
                row.append(row_multiply(self.X[i], [Z[m][j] for m in xrange(0,Z.rows)]))
            product.append(row)
        return Matrix(product)

    def __str__(self):
        """
        String representation of matrix.
        """
        return str(self.X)

    def __repr__(self):
        """
        Representation of the matrix
        """
        return str(self.X)

    @property
    def determinant(self):
        return recursive_determinant(self)

def row_multiply(r1,r2):
    """
    Multiply two vectors.  Used for matrix multiplication.
    r1 - first vector, ie [1,1]
    r2 - second vector
    """
    assert(len(r1)==len(r2))
    products =[]
    for i in xrange(0,len(r1)):
        products.append(r1[i]*r2[i])
    return sum(products)

def check_for_all_zeros(X,i,j):
    """
    Check matrix X to see if only zeros exist at or below row i in column j
    X - a list of lists
    i - row index
    j - column index
    returns -
        zero_sum - the count of non zero entries
        first_non_zero - index of the first non value
    """
    non_zeros = []
    first_non_zero = -1
    for m in xrange(i,len(X)):
        non_zero = X[m][j]!=0.0
        non_zeros.append(non_zero)
        if first_non_zero==-1 and non_zero:
            first_non_zero = m
    zero_sum = sum(non_zeros)
    return zero_sum, first_non_zero

def swap_row(X,i,p):
    """
    Swap row i and row p in a list of lists
    X - list of lists
    i - row index
    p - row index
    returns- modified matrix
    """
    X[p], X[i] = X[i], X[p]
    return X

def make_identity(r,c):
    """
    Make an identity matrix with dimensions rxc
    r - number of rows
    c - number of columns
    returns - list of lists corresponding to  the identity matrix
    """
    identity = []
    for i in xrange(0,r):
        row = []
        for j in xrange(0,c):
            elem = 0.0
            if i==j:
                elem = 1.0
            row.append(elem)
        identity.append(row)
    return identity

def invert(X):
    """
    Invert a matrix X according to gauss-jordan elimination
    In gauss-jordan elimination, we perform basic row operations to turn a matrix into
    row-echelon form.  If we concatenate an identity matrix to our input
    matrix during this process, we will turn the identity matrix into our inverse.
    X - input list of lists where each list is a matrix row
    returns - inverse of X
    """
    #copy X to avoid altering input
    X = deepcopy(X)
    #Get dimensions of X
    rows = len(X)
    cols = len(X[0])

    #Get the identity matrix and append it to the right of X
    #This is done because our row operations will make the identity into the inverse
    identity = make_identity(rows,cols)
    for i in xrange(0,rows):
        X[i]+=identity[i]

    i = 0
    for j in xrange(0,cols):
        #Check to see if there are any nonzero values below the current row in the current column
        zero_sum, first_non_zero = check_for_all_zeros(X,i,j)
        #If everything is zero, increment the columns
        if zero_sum==0:
            if j==cols:
                return X
            print "matrices con zero_sum",zero_sum
            raise Exception("Matrix is singular.")
        #If X[i][j] is 0, and there is a nonzero value below it, swap the two rows
        if first_non_zero != i:
            X = swap_row(X,i,first_non_zero)
        #Divide X[i] by X[i][j] to make X[i][j] equal 1
        X[i] = [m/X[i][j] for m in X[i]]

        #Rescale all other rows to make their values 0 below X[i][j]
        for q in xrange(0,rows):
            if q!=i:
                scaled_row = [X[q][j] * m for m in X[i]]
                X[q]= [X[q][m] - scaled_row[m] for m in xrange(0,len(scaled_row))]
        #If either of these is true, we have iterated through the matrix, and are done
        if i==rows or j==cols:
            break
        i+=1

    #Get just the right hand matrix, which is now our inverse
    for i in xrange(0,rows):
        X[i] = X[i][cols:len(X[i])]

    return X

def mean(l):
    """
    Mean of a list
    l - input list
    """
    return sum(l)/len(l)

def gje(X):
    X = deepcopy(X)
    rows = len(X)
    cols = len(X[0])

    identity = make_identity(rows,cols)
    for i in xrange(0,rows):
        X[i]+=identity[i]

    for k in xrange(0,rows):
        abs_list = [abs(X[i][k]) for i in xrange(k,rows)]
        i_max  = abs_list.index(max(abs_list))+k
        if X[i_max][k] == 0:
            raise Exception("Matrix is singular!")
        X = swap_row(X, k, i_max)
        for i in xrange(k+1, rows):
            for j in xrange(k, cols):
                X[i][j]  = X[i][j] - X[k][j] * (X[i][j] / X[j][j])
            X[i][k]  = 0

    for i in xrange(0,rows):
        X[i] = X[i][int(cols):len(X[i])]

    return X

def recursive_determinant(X):
    """
    Find the determinant in a recursive fashion.  Very inefficient
    X - Matrix object
    """
    #Must be a square matrix
    assert X.rows == X.cols
    #Must be at least 2x2
    assert X.rows > 1

    term_list = []
    #If more than 2 rows, reduce and solve in a piecewise fashion
    if X.cols>2:
        for j in xrange(0,X.cols):
            #Remove i and j columns
            new_x = deepcopy(X)
            del new_x[0]
            new_x.del_column(j)
            #Find the multiplier
            multiplier = X[0][j] * math.pow(-1,(2+j))
            #Recurse to find the determinant
            det = recursive_determinant(new_x)
            term_list.append(multiplier*det)
        return sum(term_list)
    else:
        return(X[0][0]*X[1][1] - X[0][1]*X[1][0])

