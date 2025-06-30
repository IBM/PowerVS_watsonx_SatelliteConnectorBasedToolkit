import './DataTable.css';
import PropTypes from 'prop-types';

const DataTable = ({ data }) => {
  if (!data || !data.length) return null; // Render nothing if there's no data

  const headers = Object.keys(data[0][0] || {});

  return (
    <table className="chatbot-table">
      <thead>
        <tr>
          {headers.map((header) => (
            <th key={header}>{header}</th>
          ))}
        </tr>
      </thead>
      <tbody>
        {data.flat().map((row, index) => (
          <tr key={index}>
            {headers.map((header) => (
              <td key={header}>{row[header]}</td>
            ))}
          </tr>
        ))}
      </tbody>
    </table>
  );
};

DataTable.propTypes = {
  data: PropTypes.object.isRequired
};

export default DataTable;
