#include "matrix.h"



Matrix::Matrix(std::vector< std::vector<float> > m)
{
	rowsCount = m.size();
	colsCount = m[0].size();
	mat = m;
}

Matrix::Matrix(int rows, int cols)
{
	rowsCount = rows;
	colsCount = cols;
	for(int i = 0;i <rows;i++)
	{
		for (int j = 0;j<cols; j++)
		{
			row.push_back(float(j));
		}
		mat.push_back( row );
	}
	//mat(row, std::vector<float>(col));
}

std::vector<float> Matrix::getRow( int row )
{
	return mat[row];
}

void Matrix::setValue(int row, int col, float val)
{
	mat[row][col] = val;
}

float Matrix::getValue(int row, int col)
{
	return mat[row][col];
}

Matrix::~Matrix()
{
}

Matrix Matrix::mult( Matrix m )
{
	std::vector< std::vector<float> > mRes;
	for (int i = 0; i< rowsCount; i++)
	{
		std::vector< float > mRow;
		for (int j = 0; j< m.colsCount;j++)
		{
			float res = 0;
			for( int y = 0; y < mat[i].size(); y++ )
			{
				res = res + ( mat[i][y]*m.mat[j][y] );
			}
			mRow.push_back( res );
		}
		mRes.push_back( mRow );
	}
	return Matrix( mRes );
}

Matrix Matrix::invert()
{
	Matrix X( mat );
	Matrix identity = make_identity(rowsCount, colsCount);
	for (int i = 0; i < rowsCount; i++)
	{
		for (int j = 0; j < colsCount; j++)
		{
			//fprintf(stderr, "identity[%u][%u] = %g\n",i,j,identity.getValue(i,j) );
			X.mat[i].push_back( identity.getValue( i, j ) );
		}
	}
	int i = 0;
	for (int j = 0; j < colsCount; j++)
	{
		int first_non_zero = 0;
		float zero_sum = check_for_all_zeros( X, i, j, first_non_zero );

		if (zero_sum == 0.0)
		{
			if( j == colsCount ) return X;
		}
		if (first_non_zero != i)
			X = swap_row( X, i, first_non_zero );

		std::vector< float > divX;
		for (int m = 0; m < X.mat[i].size(); m++)
		{
			divX.push_back( X.mat[i][m]/X.mat[i][j] );	
		}
		X.mat[i] = divX;
		for (int q = 0; q < rowsCount; q++)
		{
			if( q != i )
			{
				std::vector< float > scaled_row;
				for (int m = 0; m < X.mat[i].size() ; m++)
				{
					scaled_row.push_back( X.getValue(q, j) * X.mat[i][m] );
				}
				std::vector< float > temp_row;
				for (int m = 0; m < scaled_row.size(); m++)
				{
					temp_row.push_back( X.mat[q][m] - scaled_row[m] );
				}
				X.mat[q] = temp_row;
			}
		}

		if ( (i == rowsCount) || ( j == colsCount))
			break;

		i = i+1;
	}

	for (int i = 0; i < rowsCount; i++)
	{
		std::vector< float > temp_row;
		for (int m = colsCount; m < X.mat[i].size(); m++)
		{
			temp_row.push_back( X.mat[i][m] );
		}
		X.mat[i] = temp_row;
	}
	
	//fprintf(stderr, "returning ok" );
	return X;
}

Matrix Matrix::swap_row( Matrix X, int i, int p )
{
	std::vector< float > tmpI;
	std::vector< float > tmpP;
	tmpI = X.mat[i];
	tmpP = X.mat[p];
	X.mat[p] = tmpI;
	X.mat[i] = tmpP;
	return X;
}

float Matrix::check_for_all_zeros(Matrix X, int i, int j, int &first_non_zero)
{
	float zero_sum = 0;
	first_non_zero = -1;
	for (int m = i; m < X.mat.size(); m++)
	{
		bool non_zero = X.getValue(m,j)!=0.0;
		if (non_zero) zero_sum +=1.0;
		if ((first_non_zero == -1) && (non_zero))
		{
			first_non_zero = m;
		}
	}
	return zero_sum;
}

Matrix Matrix::make_identity( int rows, int cols )
{
	std::vector< std::vector<float> > matTmp;
	for(int i = 0;i <rows;i++)
	{
		std::vector< float > rowTmp;
		for (int j = 0;j<cols; j++)
		{
			float elem = 0.0;
			if (i == j) elem = 1.0;
			rowTmp.push_back( elem );
		}
		matTmp.push_back( rowTmp );
	}
	return Matrix(matTmp);
}
