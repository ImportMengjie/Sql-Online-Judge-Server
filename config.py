
HTTP_OK = 200  # 请求成功,并且处理无错误
HTTP_Created = 201  # 已创建。成功请求并创建了新的资源
HTTP_Accepted = 202  # 已接受。已经接受请求，但未处理完成
HTTP_Partial_Content = 206  # 部分内容。服务器成功处理了部分GET请求

# 400
HTTP_Bad_Request = 400  # 客户端请求的语法错误，服务器无法理解
HTTP_Unauthorized = 401  # 请求要求用户的身份认证
HTTP_Forbidden = 403  # 服务器理解请求客户端的请求，但是拒绝执行此请求
HTTP_NotFound = 404  # 没找到

# 500
HTTP_Server_Error = 500  # 服务器内部错误，无法完成请求
