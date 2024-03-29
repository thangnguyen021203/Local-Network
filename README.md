# Đây là project nho nhỏ về bài tập lớn môn học Computer Network của nhóm chúng mình
Nhóm gồm:


| Tên thành viên    | - |  Mã số sinh viên |
|-------------------|---|------------------|
| Nguyễn Quốc Thắng | - | 2114837          |
| Trần Bảo Phúc     | - | 2114452          |
| Nguyễn Minh Điềm  | - | 2111056          |
| Hồ Huy Hoàng      | - | 2110181          |

## 1. Cơ sở lý thuyết
Kiến trúc Peer-to-Peer (P2P) đặc trưng bởi việc các thiết bị kết nối và trao đổi thông tin trực tiếp với nhau, mà không cần sự can thiệp của một trung tâm điều khiển hoặc server trung gian. Trong môi  trường mạng Peer-to-Peer, không tồn tại khái niệm server và Client, tất cả các thiết bị tham gia được
coi là bình đẳng và được gọi là "peer". Mỗi peer trong mạng đóng vai trò như một nút vừa gửi thông tin và vừa nhận thông tin từ các nút khác.  
Kiến trúc P2P thường xuất hiện trong các ứng dụng chia sẻ tệp tin như BitTorrent, cũng như trong các ứng dụng trò chơi trực tuyến đa người chơi và các ứng dụng liên quan đến blockchain và tiền điện tử. Một điểm nổi bật của kiến trúc P2P là khả năng tự mở rộng, cho phép mạng linh hoạt thích ứng với sự gia tăng hoặc giảm thiểu của số lượng peer mà không cần sự can thiệp thủ công. Đồng thời, kiến trúc này cũng mang lại hiệu quả về chi phí bởi vì không đòi hỏi một kiến trúc hạ tầng lớn và băng thông cho server, một trái ngược hoàn toàn với mô hình Client-Server.  
Tuy nhiên, kiến trúc P2P cũng đối mặt với những thách thức, bao gồm vấn đề về bảo mật do tính
phân tán cao, cùng với những thách thức về hiệu suất và độ tin cậy. Điều này là do việc quản lý thông
tin và tài nguyên trong môi trường phân tán có thể gặp khó khăn và đòi hỏi sự cân nhắc cẩn thận để
giải quyết.

## 2. Các giao thức sử dụng
### Giao thức có sẵn:

> ***TCP***: sử dụng port để quản lý các ứng dụng cùng truy cập đến TCP. Mỗi process khi muốn sử dụng TCP để giao tiếp với mạng đều phải được gắn với một port, và không có 2 process nào trên cùng một máy được sử dụng chung 1 port.  
> 
> ***IP***: Hoạt động ở tầng mạng (Network Layer) trong mô hình kiến trúc năm tầng hay mô hình OSI. Có chức năng vận chuyển các gói tin trong mạng Internet. Mỗi máy sẽ được gán một địa chỉ, gọi là địa chỉ IP. Địa chỉ này được sử dụng để truyền và định tuyến từng gói thông tin bên trong mạng Internet, qua các router, và đến được máy cuối cùng. Các gói tin từ tầng Transport của một máy được truyền đến tầng Network và được IP đưa đến tầng Transport của máy ở đầu bên kia.

### Giao thức tự định nghĩa:

>***BAIEP (Brilliantly Assured Information Exchange Protoco)***:cung cấp khả năng giao tiếp giữa các peers, được thiết kế như bảng sau.  
> | Thành phần | Mục đích sử dụng |
> |------------| ------------------------------------------------| 
> | Header     | Xác định loại tin nhắn và các thông tin của peer |
> | Body       | Xác định tên file được gửi đi và nội dung gửi đi | 
  
> **Cấu trúc Header**:
> | Thành phần | Mục đích sử dụng                                    |
> |------------|-----------------------------------------------------|
> | type_msg   | Xác định loại tin nhắn                              |
> | username   | Xác định tên tài khoản người gửi khi đăng kí hoặc đăng nhập |
> | password   | Xác định mật khẩu người gửi khi đăng kí hoặc đăng nhập | 
> | port       | Xác định port của server trong mỗi peer khi đăng kí  |

>**Cấu trúc Body**:
>| Thành phần  | Mục đích sử dụng |
>|-------------|------------------|
>| file_name   | Xác định tên của file khi gửi yêu cầu hoặc nhận file |
>| content     | Truyền nội dung khi giao tiếp                          |


>**Các loại type_msg**:
>| Loại     | Mục đích sử dụng     |
>|----------|----------------------------------------------------------------------------------------------------------------------|
>| regist   | Sử dụng để Client đăng ký thông tin cho Server                                                                       |
>| login    | Sử dụng để Client đăng nhập vào mạng trao đổi file                                                                  |
>| fetch    | Sử dụng cho lệnh fetch của peer nhằm yêu cầu một danh sách các peer chứa file và cho các phản hồi fetch của Server |
>| announce | Sử dụng để thông báo file mà peer vừa tải lên repository                                                            |
>| download | Sử dụng sau khi Client lấy danh sách các peer từ lệnh fetch. Sau khi có được danh sách này, Client sẽ chọn một peer bằng command line, sau đó giao tiếp trước với peer đó bằng download message để tải file |

## 3. Hiện thực các hàm 
### Về phía Peer
> ***publish lname fname***: a local file (which is stored in the client's file system at lname) is added to the client's repository as a file named fname and this information is conveyed to the server.  
> ***fetch fname***: fetch some copy of the target file and add it to the local repository.

### Về phía Server
> ***discover hostname***: discover the list of local files of the host named hostname.  
> ***ping hostname***: live check the host named hostname.


*Kết quả*: Kết quả đạt được khá tốt với điều kiện ~25mb/s, truyền file 1.1gb với thời gian là ~ 2minutes  
*****
a
*****

