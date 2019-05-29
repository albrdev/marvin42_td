DIR_SRC				:= .
DIR_CFG				:= cfg

DIR_BIN_INSTALL		:= /usr/local/bin
DIR_CFG_INSTALL		:= /etc

TD_SRC_NAME			:= marvin42_td.py
TD_APP_NAME			:= $(basename $(TD_SRC_NAME))
TD_CFG_NAME			:= $(TD_APP_NAME)rc

CGD_SRC_NAME		:= marvin42_cgd.py
CGD_APP_NAME		:= $(basename $(CGD_SRC_NAME))
CGD_CFG_NAME		:= $(CGD_APP_NAME)rc

MOD_NAME			:= modules

CMD_CP				:= cp
CMD_RM				:= rm
CMD_CHMOD			:= chmod
CMD_PRINT			:= @printf

.PHONY: install
install:
	$(CMD_CP) --force $(DIR_SRC)/$(TD_SRC_NAME) $(DIR_BIN_INSTALL)/$(TD_APP_NAME)
	$(CMD_CP) --no-clobber $(DIR_CFG)/$(TD_CFG_NAME) $(DIR_CFG_INSTALL)/$(TD_CFG_NAME)

	$(CMD_CP) --force $(DIR_SRC)/$(CGD_SRC_NAME) $(DIR_BIN_INSTALL)/$(CGD_APP_NAME)
	$(CMD_CP) --no-clobber $(DIR_CFG)/$(CGD_CFG_NAME) $(DIR_CFG_INSTALL)/$(CGD_CFG_NAME)

	$(CMD_CP) --recursive --no-target-directory --force $(DIR_SRC)/$(MOD_NAME) $(DIR_BIN_INSTALL)/$(MOD_NAME)

	$(CMD_CHMOD) u+x,g+x $(DIR_BIN_INSTALL)/$(TD_APP_NAME)
	$(CMD_CHMOD) u+x,g+x $(DIR_BIN_INSTALL)/$(CGD_APP_NAME)

.PHONY: uninstall
uninstall:
	$(CMD_RM) --recursive --force $(DIR_BIN_INSTALL)/$(MOD_NAME)
	$(CMD_RM) --force $(DIR_BIN_INSTALL)/$(TD_APP_NAME)
	$(CMD_RM) --force $(DIR_BIN_INSTALL)/$(CGD_APP_NAME)

.PHONY: test
test:
	$(CMD_PRINT) "DIR_SRC=$(DIR_SRC)\n"
	$(CMD_PRINT) "DIR_CFG=$(DIR_CFG)\n"
	$(CMD_PRINT) "DIR_BIN_INSTALL=$(DIR_BIN_INSTALL)\n"
	$(CMD_PRINT) "DIR_CFG_INSTALL=$(DIR_CFG_INSTALL)\n"
	$(CMD_PRINT) "TD_SRC_NAME=$(TD_SRC_NAME)\n"
	$(CMD_PRINT) "TD_APP_NAME=$(TD_APP_NAME)\n"
	$(CMD_PRINT) "TD_CFG_NAME=$(TD_CFG_NAME)\n"
	$(CMD_PRINT) "CGD_SRC_NAME=$(CGD_SRC_NAME)\n"
	$(CMD_PRINT) "CGD_APP_NAME=$(CGD_APP_NAME)\n"
	$(CMD_PRINT) "CGD_CFG_NAME=$(CGD_CFG_NAME)\n"
	$(CMD_PRINT) "MOD_NAME=$(MOD_NAME)\n"
