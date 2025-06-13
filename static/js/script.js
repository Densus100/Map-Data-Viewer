$(document).ready(function () {
  var table = $(".dynamic-table").DataTable({
    scrollX: true, // Mengaktifkan scroll horizontal
    autoWidth: false, // Mencegah lebar kolom menjadi tidak proporsional
  });

  $("#table_tingkat").DataTable({
    scrollX: true, // Mengaktifkan scroll horizontal
    autoWidth: false, // Mencegah lebar kolom menjadi tidak proporsional
  });
  $("#table_lokasi").DataTable({
    scrollX: true, // Mengaktifkan scroll horizontal
    autoWidth: false, // Mencegah lebar kolom menjadi tidak proporsional
  });
  $("#table_provinsi").DataTable({
    scrollX: true, // Mengaktifkan scroll horizontal
    autoWidth: false, // Mencegah lebar kolom menjadi tidak proporsional
  });
  $("#table_status").DataTable({
    scrollX: true, // Mengaktifkan scroll horizontal
    autoWidth: false, // Mencegah lebar kolom menjadi tidak proporsional
  });
  $("#table_jeniskelamin").DataTable({
    scrollX: true, // Mengaktifkan scroll horizontal
    autoWidth: false, // Mencegah lebar kolom menjadi tidak proporsional
  });

  // Use browser's IP for the request (this assumes you are using the correct network)
  var serverIP = window.location.hostname; // This will dynamically fetch the IP of the server

  const validUsername = "admin";
  let validPassword = "123";

  $("#file-upload-btn").click(function () {
    const username = prompt("Enter Username:");
    let password = prompt("Enter password: ");

    if (username === validUsername && password === validPassword) {
      $("#file-upload").click();
    } else {
      alert("Username atau Password salah. Anda tidak dapat mengupload data.");
    }
  });

  $("#file-upload").change(function (event) {
    var file = event.target.files[0];
    if (!file) return;

    var formData = new FormData();
    formData.append("file", file);

    setTimeout(() => {
      $("#loading-overlay").fadeIn("slow"); // Hide spinner after the page is ready
    }, 1000);

    $.ajax({
      url: `http://${serverIP}:3000/upload`, // ✅ Gunakan template literal
      method: "POST",
      data: formData,
      contentType: false,
      processData: false,
      success: function (response) {
        setTimeout(() => {
          $("#loading-overlay").fadeOut("slow"); // Hide spinner after the page is ready
        }, 1000);

        alert("File berhasil di-upload dan diproses!");
        location.reload();
      },
      error: function (error) {
        setTimeout(() => {
          $("#loading-overlay").fadeOut("slow"); // Hide spinner after the page is ready
        }, 1000);

        console.error("Terjadi error saat upload:", error);
        alert("Gagal upload file.");
        location.reload();
      },
    });
  });

  function loadExcelFromServer() {
    fetch(`http://${serverIP}:3000/uploads/excel-file/last-update`)
      .then((response) => response.json())
      .then((data) => {
        return new Promise((resolve) => {
          setTimeout(() => {
            resolve(data);
          }, 500); // Tambahkan delay agar loading terlihat
        });
      })
      .then((data) => {
        $("#last-update").text(new Date(data.lastModified).toLocaleString());
        return fetch(`http://${serverIP}:3000/uploads/excel-file`);
      })
      .then((response) => response.arrayBuffer())
      .then((buffer) => {
        var data = new Uint8Array(buffer);
        var workbook = XLSX.read(data, { type: "array" });
        var sheet = workbook.Sheets[workbook.SheetNames[0]];
        var jsonData = XLSX.utils.sheet_to_json(sheet, { header: 1 });

        var headerRow = jsonData[0];

        // Destroy existing DataTable if it exists
        if ($.fn.DataTable.isDataTable('.dynamic-table')) {
          $('.dynamic-table').DataTable().destroy();
        }

        // Clear and rebuild table head and body
        $(".dynamic-table thead").empty().append(`
          <tr>${headerRow.map((col) => `<th class="text-center">${col}</th>`).join("")}</tr>
        `);
        $(".dynamic-table tbody").empty(); // Clear body too

        // Insert new data rows
        jsonData.slice(1).forEach((row) => {
          var rowData = headerRow.map((_, i) => row[i] !== undefined ? row[i] : "");
          $(".dynamic-table tbody").append(`
            <tr>${rowData.map((cell) => `<td class="text-center">${cell}</td>`).join("")}</tr>
          `);
        });

        // Reinitialize DataTable
        table = $(".dynamic-table").DataTable({
          scrollX: true, // Optional: make table responsive
          autoWidth: false,  // Optional: prevent automatic width calc
        });

        if (headerRow[0] != "File not found.") {
          let modelDownloadLink = `http://${serverIP}:3000/uploads/data_view.xlsx`;
          $(`#view-download-link`).attr("href", modelDownloadLink);
        }

      })
      .catch((error) => {
        console.error("Error reading file: ", error);
        $("#last-update").html("File Not Found! <br>Please upload a new one.");
      });
  }

  loadExcelFromServer();

  function loadViewTingkat() {
    fetch(`http://${serverIP}:3000/uploads/excel-file/data_view_tingkat`)
      .then((response) => response.arrayBuffer())
      .then((buffer) => {
        var data = new Uint8Array(buffer);
        var workbook = XLSX.read(data, { type: "array" });
        var sheet = workbook.Sheets[workbook.SheetNames[0]];
        var jsonData = XLSX.utils.sheet_to_json(sheet, { header: 1 });

        var headerRow = jsonData[0];
        // Destroy existing DataTable if it exists
        if ($.fn.DataTable.isDataTable('#table_tingkat')) {
          $('#table_tingkat').DataTable().destroy();
        }

        // Clear and rebuild table head and body
        $("#table_tingkat thead").empty().append(`
          <tr>${headerRow.map((col) => `<th class="text-center">${col}</th>`).join("")}</tr>
        `);
        $("#table_tingkat tbody").empty(); // Clear body too

        // Insert new data rows
        jsonData.slice(1).forEach((row) => {
          var rowData = headerRow.map((_, i) => row[i] !== undefined ? row[i] : "");
          $("#table_tingkat tbody").append(`
            <tr>${rowData.map((cell) => `<td class="text-center">${cell}</td>`).join("")}</tr>
          `);
        });

        // Reinitialize DataTable
        $("#table_tingkat").DataTable({
          scrollX: true, // Optional: make table responsive
          autoWidth: false,  // Optional: prevent automatic width calc
        });


        if (headerRow[0] != "File not found.") {
          let modelDownloadLink = `http://${serverIP}:3000/uploads/data_view_tingkat.xlsx`;
          $(`#tingkat-download-link`).attr("href", modelDownloadLink);
        }

      })
      .catch((error) => {
        console.error("Error reading file: ", error);
      });
  }

  function loadViewLokasi() {
    fetch(`http://${serverIP}:3000/uploads/excel-file/data_view_lokasi`)
      .then((response) => response.arrayBuffer())
      .then((buffer) => {
        var data = new Uint8Array(buffer);
        var workbook = XLSX.read(data, { type: "array" });
        var sheet = workbook.Sheets[workbook.SheetNames[0]];
        var jsonData = XLSX.utils.sheet_to_json(sheet, { header: 1 });

        var headerRow = jsonData[0];
        // Destroy existing DataTable if it exists
        if ($.fn.DataTable.isDataTable('#table_lokasi')) {
          $('#table_lokasi').DataTable().destroy();
        }

        // Clear and rebuild table head and body
        $("#table_lokasi thead").empty().append(`
          <tr>${headerRow.map((col) => `<th class="text-center">${col}</th>`).join("")}</tr>
        `);
        $("#table_lokasi tbody").empty(); // Clear body too

        // Insert new data rows
        jsonData.slice(1).forEach((row) => {
          var rowData = headerRow.map((_, i) => row[i] !== undefined ? row[i] : "");
          $("#table_lokasi tbody").append(`
            <tr>${rowData.map((cell) => `<td class="text-center">${cell}</td>`).join("")}</tr>
          `);
        });

        // Reinitialize DataTable
        $("#table_lokasi").DataTable({
          scrollX: true, // Optional: make table responsive
          autoWidth: false,  // Optional: prevent automatic width calc
        });

        if (headerRow[0] != "File not found.") {
          let modelDownloadLink = `http://${serverIP}:3000/uploads/data_view_lokasi.xlsx`;
          $(`#lokasi-download-link`).attr("href", modelDownloadLink);
        }

      })
      .catch((error) => {
        console.error("Error reading file: ", error);
      });
  }
  function loadViewProvinsi() {
    fetch(`http://${serverIP}:3000/uploads/excel-file/data_view_provinsi`)
      .then((response) => response.arrayBuffer())
      .then((buffer) => {
        var data = new Uint8Array(buffer);
        var workbook = XLSX.read(data, { type: "array" });
        var sheet = workbook.Sheets[workbook.SheetNames[0]];
        var jsonData = XLSX.utils.sheet_to_json(sheet, { header: 1 });

        var headerRow = jsonData[0];
        // Destroy existing DataTable if it exists
        if ($.fn.DataTable.isDataTable('#table_provinsi')) {
          $('#table_provinsi').DataTable().destroy();
        }

        // Clear and rebuild table head and body
        $("#table_provinsi thead").empty().append(`
          <tr>${headerRow.map((col) => `<th class="text-center">${col}</th>`).join("")}</tr>
        `);
        $("#table_provinsi tbody").empty(); // Clear body too

        // Insert new data rows
        jsonData.slice(1).forEach((row) => {
          var rowData = headerRow.map((_, i) => row[i] !== undefined ? row[i] : "");
          $("#table_provinsi tbody").append(`
            <tr>${rowData.map((cell) => `<td class="text-center">${cell}</td>`).join("")}</tr>
          `);
        });

        // Reinitialize DataTable
        $("#table_provinsi").DataTable({
          scrollX: true, // Optional: make table responsive
          autoWidth: false,  // Optional: prevent automatic width calc
        });

        if (headerRow[0] != "File not found.") {
          let modelDownloadLink = `http://${serverIP}:3000/uploads/data_view_provinsi.xlsx`;
          $(`#provinsi-download-link`).attr("href", modelDownloadLink);
        }

      })
      .catch((error) => {
        console.error("Error reading file: ", error);
      });
  }

  function loadViewStatus() {
    fetch(`http://${serverIP}:3000/uploads/excel-file/data_view_status`)
      .then((response) => response.arrayBuffer())
      .then((buffer) => {
        var data = new Uint8Array(buffer);
        var workbook = XLSX.read(data, { type: "array" });
        var sheet = workbook.Sheets[workbook.SheetNames[0]];
        var jsonData = XLSX.utils.sheet_to_json(sheet, { header: 1 });

        var headerRow = jsonData[0];
        // Destroy existing DataTable if it exists
        if ($.fn.DataTable.isDataTable('#table_status')) {
          $('#table_status').DataTable().destroy();
        }

        // Clear and rebuild table head and body
        $("#table_status thead").empty().append(`
          <tr>${headerRow.map((col) => `<th class="text-center">${col}</th>`).join("")}</tr>
        `);
        $("#table_status tbody").empty(); // Clear body too

        // Insert new data rows
        jsonData.slice(1).forEach((row) => {
          var rowData = headerRow.map((_, i) => row[i] !== undefined ? row[i] : "");
          $("#table_status tbody").append(`
            <tr>${rowData.map((cell) => `<td class="text-center">${cell}</td>`).join("")}</tr>
          `);
        });

        // Reinitialize DataTable
        $("#table_status").DataTable({
          scrollX: true, // Optional: make table responsive
          autoWidth: false,  // Optional: prevent automatic width calc
        });

        if (headerRow[0] != "File not found.") {
          let modelDownloadLink = `http://${serverIP}:3000/uploads/data_view_status.xlsx`;
          $(`#status-download-link`).attr("href", modelDownloadLink);
        }

      })
      .catch((error) => {
        console.error("Error reading file: ", error);
      });
  }

  function loadViewJenisKelamin() {
    fetch(`http://${serverIP}:3000/uploads/excel-file/data_view_jeniskelamin`)
      .then((response) => response.arrayBuffer())
      .then((buffer) => {
        var data = new Uint8Array(buffer);
        var workbook = XLSX.read(data, { type: "array" });
        var sheet = workbook.Sheets[workbook.SheetNames[0]];
        var jsonData = XLSX.utils.sheet_to_json(sheet, { header: 1 });

        var headerRow = jsonData[0];
        // Destroy existing DataTable if it exists
        if ($.fn.DataTable.isDataTable('#table_jeniskelamin')) {
          $('#table_jeniskelamin').DataTable().destroy();
        }

        // Clear and rebuild table head and body
        $("#table_jeniskelamin thead").empty().append(`
          <tr>${headerRow.map((col) => `<th class="text-center">${col}</th>`).join("")}</tr>
        `);
        $("#table_jeniskelamin tbody").empty(); // Clear body too

        // Insert new data rows
        jsonData.slice(1).forEach((row) => {
          var rowData = headerRow.map((_, i) => row[i] !== undefined ? row[i] : "");
          $("#table_jeniskelamin tbody").append(`
            <tr>${rowData.map((cell) => `<td class="text-center">${cell}</td>`).join("")}</tr>
          `);
        });

        // Reinitialize DataTable
        $("#table_jeniskelamin").DataTable({
          scrollX: true, // Optional: make table responsive
          autoWidth: false,  // Optional: prevent automatic width calc
        });

        if (headerRow[0] != "File not found.") {
          let modelDownloadLink = `http://${serverIP}:3000/uploads/data_view_jeniskelamin.xlsx`;
          $(`#jeniskelamin-download-link`).attr("href", modelDownloadLink);
        }

      })
      .catch((error) => {
        console.error("Error reading file: ", error);
      });
  }

  loadViewTingkat();
  loadViewLokasi();
  loadViewProvinsi();
  loadViewStatus();
  loadViewJenisKelamin();

  function loadModelTable(tab) {

    var model = false;

    if (tab == "tab1") {
      model = "kmeans";
    } else if (tab == "tab2") {
      model = "gmm";
    } else if (tab == "tab3") {
      model = "hierarchical";
    } else if (tab == "tab4") {
      model = "kmeans_elbow";
    } else if (tab == "tab5") {
      model = "gmm_elbow";
    } else if (tab == "tab6") {
      model = "hierarchical_elbow";
    }

    $(`#load-${model}-table`).click(function (event) {
      event.preventDefault();
      let fileUrl = `http://${serverIP}:3000/uploads/${model}_model/${model}_output.csv`; // Adjust file path if needed
      let tableContainer = $(`#${model}_output_container`); // This is where the table will be created

      // Show loading spinner
      tableContainer.html(`
            <p class="text-center">Loading data...<br>
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
            </p>
        `);

      // Fetch CSV file and process it
      fetch(fileUrl)
        .then((response) => response.arrayBuffer()) // Read as binary buffer
        .then((buffer) => {
          let data = new Uint8Array(buffer);
          let workbook = XLSX.read(data, { type: "array" });
          let sheet = workbook.Sheets[workbook.SheetNames[0]];
          let jsonData = XLSX.utils.sheet_to_json(sheet, { header: 1 });

          let headerRow = jsonData[0]; // Extract header row

          // ✅ Create the table dynamically inside the container
          tableContainer.html(`
                    <table id="${model}_output" class="display output_result_tab2" style="width:100%">
                        <thead>
                            <tr>${headerRow
              .map(
                (col) => `<th class="text-center">${col}</th>`
              )
              .join("")}</tr>
                        </thead>
                        <tbody></tbody>
                    </table>
                `);

          let table = $(`#${model}_output`).DataTable({
            scrollX: true,
            autoWidth: false,
          }); // Initialize DataTable

          // ✅ Insert table rows
          jsonData.slice(1).forEach((row) => {
            let rowData = headerRow.map((_, i) =>
              row[i] !== undefined ? row[i] : ""
            );
            if (rowData.length === headerRow.length) {
              table.row.add(rowData);
            }
          });

          // ✅ Redraw the table
          table.draw();

          // ✅ Remove the loading spinner
          tableContainer.find(".spinner-border").remove();
        })
        .catch((error) => {
          console.error("Error loading CSV:", error);
          tableContainer.html("<p class='text-danger'>Failed to load CSV.</p>");
        });
    });
  }

  // Sembunyikan tombol reset saat halaman pertama dimuat
  // $("#reset-filter").hide();

  $("area").on("click", function (event) {
    event.preventDefault();
    const city = $(this).data("city");
    $("#selected-city").text("Filter Kota: " + city);

    table.column(3).search(city).draw();
    if (city) {
      $("#reset-filter").show();
    }
  });

  $("#reset-filter").on("click", function () {
    $("#selected-city").text("Menampilkan Semua Kota");
    table.column(3).search("").draw(); // Menghapus filter

    // ✅ Perbaikan: gunakan `$(this)`, bukan `$$(this)`
    // $(this).hide();
  });

  table.on("draw", function () {
    let filterApplied = table.column(3).search() !== "";
    $("#reset-filter").toggle(filterApplied);
  });

  function checkExistingImages(tab) {
    let imagesDiv = $(`#images-${tab}`); // Pilih container gambar sesuai tab
    let outputDiv = $(`#output-${tab}`); // Pilih container teks sesuai tab

    var model = false;

    if (tab == "tab1") {
      model = "kmeans";
    } else if (tab == "tab2") {
      model = "gmm";
    } else if (tab == "tab3") {
      model = "hierarchical";
    } else if (tab == "tab4") {
      model = "kmeans_elbow";
    } else if (tab == "tab5") {
      model = "gmm_elbow";
    } else if (tab == "tab6") {
      model = "hierarchical_elbow";
    }

    // 🔍 Check if images & content are already present
    let hasImages = imagesDiv.find("img").length > 0;
    let hasText = outputDiv.text().trim().length > 0;

    if (hasImages && hasText) {
      console.log(`Skipping fetch for ${tab}: Content already loaded.`);
      return; // ✅ Stop fetching if content exists
    }

    // 🔄 Show loading spinner while fetching
    outputDiv.html(`
      <p class="text-center">Loading content...<br>
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">Loading...</span>
        </div>
      </p>
    `);

    outputDiv.css("display", "inline");

    fetch(`http://${serverIP}:3000/check-existing-images/${tab}`)
      .then((response) => response.json())
      .then((data) => {
        imagesDiv.empty(); // Bersihkan gambar sebelumnya
        outputDiv.empty(); // Bersihkan teks sebelumnya

        // Handle gambar
        if (data.images.length > 0) {
          imagesDiv.show(); // Tampilkan container gambar
          $(`#${model}-download-btn`).show();
          data.images.forEach((img) => {
            imagesDiv.append(
              `<img src="http://${serverIP}:3000/uploads/${img}" style="max-width: 50%;" class="img-fluid mb-3">`
            );
          });
        } else {
          $(`#${model}-download-btn`).hide();
          imagesDiv.hide(); // Sembunyikan jika tidak ada gambar
        }

        // Handle teks
        if (data.text) {
          // Tampilkan tabel hasil
          outputDiv.html(`<pre>${data.text}</pre>`); // Menampilkan isi file dalam elemen <pre>

          // Pastikan DataTable diinisialisasi ulang dengan benar
          if ($.fn.DataTable.isDataTable(`.output_result_${tab}`)) {
            $(`.output_result_${tab}`).DataTable().destroy();
          }
          $(`.output_result_${tab}`).DataTable({
            scrollX: true,
            // autoWidth: false,
          });
          outputDiv.show(); // Tampilkan teks jika ada
        } else {
          outputDiv.hide(); // Sembunyikan jika tidak ada teks
        }

        if (data.text) {
          let modelDownloadLink = `http://${serverIP}:3000/uploads/${model}_model/${model}_output.csv`;
          $(`#${model}-download-link`).attr("href", modelDownloadLink);
          loadModelTable(tab);
        }
      })
      .catch((error) => console.error("Error checking images:", error));
  }

  // Cek gambar saat halaman pertama dimuat (default tab1)
  checkExistingImages("tab1");

  // Event listener ketika tab diklik
  $(".nav-link").on("click", function () {
    let selectedTab = $(this).attr("id").replace("-tab", ""); // Ambil tab yang diklik
    checkExistingImages(selectedTab); // Panggil fungsi sesuai tab
  });

  $(".load-result-btn").click(function (event) {
    event.preventDefault();
    var tab = $(this).data("tab");

    var model = false;

    if (tab == "tab1") {
      model = "kmeans";
    } else if (tab == "tab2") {
      model = "gmm";
    } else if (tab == "tab3") {
      model = "hierarchical";
    } else if (tab == "tab4") {
      model = "kmeans_elbow";
    } else if (tab == "tab5") {
      model = "gmm_elbow";
    } else if (tab == "tab6") {
      model = "hierarchical_elbow";
    }

    $("#loading-overlay").fadeIn("slow");

    let imagesDiv = $(`#images-${tab}`);
    imagesDiv.empty();

    var outputDiv = $(`#output-${tab}`);

    // Show loading animation FIRST before fetching data
    outputDiv.html(`
      <p class="text-center">Generating data...<br>
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">Loading...</span>
        </div>
      </p>
    `);
    outputDiv.css("display", "inline");

    // Delay the fetch slightly to ensure the spinner is rendered first
    fetch(`http://${serverIP}:3000/load-content/${tab}`)
      .then((response) => response.json()) // Ubah response menjadi JSON
      .then((data) => {
        outputDiv.empty(); // Bersihkan loading

        // Tampilkan gambar hasil model
        let existingImages = imagesDiv
          .find("img")
          .map(function () {
            return $(this).attr("src");
          })
          .get();

        data.images.forEach((img) => {
          let imgSrc = `http://${serverIP}:3000/uploads/${img}`;
          if (!existingImages.includes(imgSrc)) {
            imagesDiv.append(
              `<img src="${imgSrc}" style="max-width: 50%;" class="img-fluid mb-3">`
            );
          }
        });

        imagesDiv.show(); // Pastikan container gambar tampil
        outputDiv.show();
        $("#loading-overlay").fadeOut("slow");

        // Tampilkan tabel hasil
        outputDiv.html(`<pre>${data.content}</pre>`); // Menampilkan isi file dalam elemen <pre>

        // Pastikan DataTable diinisialisasi ulang dengan benar
        if ($.fn.DataTable.isDataTable(`.output_result_${tab}`)) {
          $(`.output_result_${tab}`).DataTable().destroy();
        }
        $(`.output_result_${tab}`).DataTable({
          scrollX: true,
          // autoWidth: false,
        });

        if (data.content) {
          let modelDownloadLink = `http://${serverIP}:3000/uploads/${model}_model/${model}_output.csv`;
          $(`#${model}-download-link`).attr("href", modelDownloadLink);
          loadModelTable(tab);
        }
      })
      .catch((error) => {
        console.error("Error:", error);
        outputDiv.html("<p class='text-danger'>Failed to load data.</p>");
      });
  });

  $(".download-pdf-btn").click(function (event) {
    event.preventDefault();

    var tab = $(this).data("tab");
    var model = "";

    if (tab == "tab1") {
      model = "kmeans";
    } else if (tab == "tab2") {
      model = "gmm";
    } else if (tab == "tab3") {
      model = "hierarchical";
    } else if (tab == "tab4") {
      model = "kmeans_elbow";
    }

    $("#loading-overlay").fadeIn("slow"); // Show spinner


    // Fetch request to generate PDF and download it
    fetch(`http://${serverIP}:3000/run-${model}-pdf`)
      .then((response) => response.blob()) // Get the response as a Blob (PDF file)
      .then((blob) => {
        const link = document.createElement("a");
        link.href = URL.createObjectURL(blob);
        link.download = `${model}_report.pdf`;
        link.click();

        // Reset the content of #myTabContent after download starts
        $("#loading-overlay").fadeOut("slow");


      })
      .catch((error) => {
        console.error("Error:", error);
        alert("There was an error generating the PDF.");

        // Reset the content of #myTabContent in case of error
        // tabContentContainer.html(
        //   "<p class='text-danger'>There was an error generating the PDF.</p>"
        // );
      });
  });

  setTimeout(() => {
    $("#loading-overlay").fadeOut("slow"); // Hide spinner after the page is ready
  }, 1000); // Adjust time as needed
});
