#include <vector>

class Matrix
{
public:
	 Matrix(int rows, int cols);
	 Matrix(std::vector< std::vector<float> > m); 
	 ~Matrix();
	float getValue(int row, int col);
	void setValue(int row, int col, float val);
	Matrix mult( Matrix m );
	Matrix make_identity( int rows, int cols );
	float check_for_all_zeros(Matrix X, int i, int j, int &first_non_zero);
	Matrix swap_row( Matrix X, int i, int p );
	std::vector<float> getRow( int row );	
	Matrix invert();
	int rowsCount;
	int colsCount;
	std::vector< std::vector<float> > mat;
	std::vector< float > row;
};

