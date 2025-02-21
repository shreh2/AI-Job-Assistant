import React from "react";

export default function FileUpload({ label, onUpload }) {
  const handleChange = (event) => {
    const file = event.target.files[0];
    if (file) {
      onUpload(file);
    }
  };

  return (
    <div>
      <input type="file" onChange={handleChange} className="form-control" />
    </div>
  );
}
